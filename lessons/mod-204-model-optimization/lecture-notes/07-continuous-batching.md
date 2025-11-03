# Lecture 07: Continuous Batching and KV Cache Management

## Learning Objectives

By the end of this lecture, you will be able to:

- Design iteration-level scheduling systems for continuous batching that dynamically admit new requests, generate tokens for running requests, and remove finished requests achieving near 100% GPU utilization
- Implement block-based KV cache management with memory pooling that allocates/frees fixed-size blocks dynamically avoiding memory fragmentation and enabling efficient memory sharing
- Architect PagedAttention CUDA kernels that compute attention correctly over non-contiguous memory blocks with block-level parallelism, warp-level softmax, and optimized memory access patterns
- Configure request scheduling algorithms (FCFS, Shortest-Job-First, priority-based) that balance latency, throughput, and fairness while preventing head-of-line blocking and starvation
- Implement preemption mechanisms that swap low-priority requests to CPU or recompute from prompt when memory pressure occurs enabling graceful handling of memory exhaustion
- Design admission control policies that evaluate available memory, current batch size, and request priority to determine when to admit new requests vs queue/preempt existing ones
- Optimize continuous batching performance through adaptive batch size tuning, dynamic block size adjustment based on workload analysis, and comprehensive metrics tracking
- Build complete production continuous batching engines integrating scheduling, memory management, preemption, and monitoring achieving 2-10x throughput improvement over static batching

## Table of Contents
1. [Introduction to Continuous Batching](#introduction)
2. [Traditional vs Continuous Batching](#traditional-vs-continuous)
3. [Iteration-Level Scheduling](#iteration-level)
4. [KV Cache Management](#kv-cache)
5. [PagedAttention Deep Dive](#pagedattention)
6. [Request Scheduling Algorithms](#scheduling)
7. [Memory Pool Management](#memory-pool)
8. [Preemption and Swapping](#preemption)
9. [Performance Optimization](#performance)
10. [Implementation Patterns](#implementation)

<a name="introduction"></a>
## 1. Introduction to Continuous Batching

Continuous batching is the key innovation enabling high-throughput LLM serving. It addresses the fundamental challenge of autoregressive generation: requests finish at different times.

### The Problem with Static Batching

```python
# Static batching: All requests start and end together
batch = [req1, req2, req3, req4]  # All start together

# Generation
for step in range(max_tokens):
    logits = model(batch)
    next_tokens = sample(logits)
    batch.append(next_tokens)

    # Problem: Some requests finish early
    if req2.finished:  # Finished at step 10
        # But we must continue for longest request
        pass  # Wasted computation on finished request

# All 4 requests occupy GPU until longest one finishes
# Huge waste if lengths vary (10 tokens vs 500 tokens)
```

**Inefficiency**: GPU time wasted on padded/finished requests.

### Continuous Batching Solution

```python
# Continuous batching: Dynamically adjust batch
running_batch = []

while True:
    # Add new requests as space becomes available
    while memory_available() and request_queue.not_empty():
        new_request = request_queue.get()
        running_batch.append(new_request)

    # Generate next token for all running requests
    logits = model(running_batch)
    next_tokens = sample(logits)

    # Remove finished requests immediately
    finished = [req for req in running_batch if req.is_finished()]
    running_batch = [req for req in running_batch if not req.is_finished()]

    # Free memory for finished requests
    for req in finished:
        free_memory(req.kv_cache)

    # Batch size adjusts automatically!
```

**Efficiency**: Near 100% GPU utilization, minimal wasted computation.

<a name="traditional-vs-continuous"></a>
## 2. Traditional vs Continuous Batching

### 2.1 Throughput Comparison

**Static Batching**:
```
Request timeline (batch_size=4, max_tokens=100):

Req1: ████████████████████ (20 tokens) ░░░░░░░░░░░░░░░░░░░░░░░░
Req2: ████████████████████████████████ (30 tokens) ░░░░░░░░░░░░
Req3: ██████████████████████████████████████████ (40 tokens) ░░
Req4: ██████████████████████████████████████████████████████ (60 tokens)

Time: 60 steps (limited by longest request)
GPU utilization: 50% (many wasted cycles on finished requests)
Throughput: 150 tokens / 60 steps = 2.5 tokens/step
```

**Continuous Batching**:
```
Request timeline (dynamic batch):

Req1: ████████████████████ (20 tokens)
Req2:     ████████████████████████████████ (30 tokens)
Req3:         ██████████████████████████████████████████ (40 tokens)
Req4:             ██████████████████████████████████████████████████ (60 tokens)
Req5:                 ████████████████████████ (25 tokens)
Req6:                     ████████████████████████████ (28 tokens)

Time: 60 steps (same)
GPU utilization: 95% (always processing active requests)
Throughput: 203 tokens / 60 steps = 3.4 tokens/step (36% improvement!)
```

### 2.2 Latency Comparison

**Static Batching**:
- Request must wait for full batch to fill
- Waiting time: 0 to `batch_fill_time`
- Average waiting: `batch_fill_time / 2`
- High variance in latency

**Continuous Batching**:
- Request starts immediately (if memory available)
- No waiting for batch to fill
- Low latency variance
- Predictable performance

<a name="iteration-level"></a>
## 3. Iteration-Level Scheduling

Continuous batching makes scheduling decisions at each iteration (token generation step).

### 3.1 Scheduling Loop

```python
class ContinuousBatchScheduler:
    def __init__(self, model, max_batch_size=128):
        self.model = model
        self.max_batch_size = max_batch_size
        self.running_requests = []
        self.waiting_queue = deque()
        self.memory_pool = KVCacheMemoryPool()

    def step(self):
        """Single iteration of continuous batching"""

        # 1. Try to add new requests from queue
        while (len(self.running_requests) < self.max_batch_size and
               self.waiting_queue and
               self.memory_pool.can_allocate()):

            new_request = self.waiting_queue.popleft()
            self.running_requests.append(new_request)

            # Allocate KV cache for new request
            new_request.kv_cache = self.memory_pool.allocate(
                num_blocks=estimate_blocks_needed(new_request)
            )

        if not self.running_requests:
            return  # No active requests

        # 2. Prepare batch input
        batch_input_ids = [req.next_token_id for req in self.running_requests]
        batch_kv_caches = [req.kv_cache for req in self.running_requests]

        # 3. Forward pass (all requests in parallel)
        outputs = self.model.forward(
            input_ids=batch_input_ids,
            kv_caches=batch_kv_caches
        )

        # 4. Sample next tokens
        for req, output in zip(self.running_requests, outputs):
            next_token = sample_token(output.logits, req.sampling_params)
            req.append_token(next_token)

            # Update KV cache (grows by 1 block if needed)
            if req.needs_more_blocks():
                if self.memory_pool.can_allocate():
                    req.kv_cache.extend(self.memory_pool.allocate(1))
                else:
                    # Out of memory: preempt this request
                    self.preempt_request(req)

        # 5. Remove finished requests
        finished_requests = [req for req in self.running_requests
                            if req.is_finished()]

        for req in finished_requests:
            self.memory_pool.free(req.kv_cache)
            self.running_requests.remove(req)
            self.return_result(req)

    def run(self):
        """Main serving loop"""
        while True:
            self.step()
```

### 3.2 Admission Control

Decide whether to admit new requests:

```python
def should_admit_request(self, request):
    """
    Decide if new request can be admitted

    Factors:
    - Available memory
    - Current batch size
    - Estimated request length
    - Priority level
    """
    # Check batch size limit
    if len(self.running_requests) >= self.max_batch_size:
        return False

    # Estimate memory needed
    estimated_tokens = min(request.max_tokens, 512)  # Conservative estimate
    blocks_needed = (estimated_tokens + self.block_size - 1) // self.block_size

    # Check if memory available
    if not self.memory_pool.can_allocate(blocks_needed):
        # Try preemption to free memory
        if self.can_preempt_for(blocks_needed):
            self.preempt_lowest_priority_requests(blocks_needed)
            return True
        return False

    return True
```

<a name="kv-cache"></a>
## 4. KV Cache Management

Efficient KV cache management is critical for serving performance.

### 4.1 KV Cache Structure

```python
class KVCache:
    """
    KV cache for single request

    Storage: List of blocks (non-contiguous memory)
    Each block stores: [num_layers, 2, block_size, num_heads, head_dim]
                        (2 for Key and Value)
    """
    def __init__(self, num_layers, num_heads, head_dim, block_size):
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.block_size = block_size
        self.blocks = []  # List of block IDs
        self.num_tokens = 0

    def append_token(self, key, value):
        """Add KV for one new token"""
        # Check if current block is full
        if self.num_tokens % self.block_size == 0:
            # Need new block
            new_block = allocate_block()
            self.blocks.append(new_block)

        # Write to current block
        block_idx = self.num_tokens // self.block_size
        in_block_idx = self.num_tokens % self.block_size

        for layer in range(self.num_layers):
            write_to_block(
                self.blocks[block_idx],
                layer,
                in_block_idx,
                key[layer],
                value[layer]
            )

        self.num_tokens += 1

    def get_kv_for_layer(self, layer):
        """Retrieve all KV for a layer (may span multiple blocks)"""
        keys = []
        values = []

        for block_id in self.blocks:
            k, v = read_from_block(block_id, layer)
            keys.append(k)
            values.append(v)

        # Concatenate across blocks
        keys = torch.cat(keys, dim=0)[:self.num_tokens]
        values = torch.cat(values, dim=0)[:self.num_tokens]

        return keys, values
```

### 4.2 Block Management

```python
class BlockMemoryPool:
    """
    Memory pool for KV cache blocks

    Uses physical block pool (like OS memory pages)
    """
    def __init__(self, num_blocks, block_size, device='cuda'):
        self.block_size = block_size
        self.device = device

        # Pre-allocate all blocks
        self.blocks = [
            self._allocate_physical_block()
            for _ in range(num_blocks)
        ]

        # Track free blocks
        self.free_blocks = set(range(num_blocks))
        self.used_blocks = {}  # request_id -> list of block_ids

    def _allocate_physical_block(self):
        """Allocate single physical block"""
        return torch.zeros(
            (num_layers, 2, self.block_size, num_heads, head_dim),
            dtype=torch.float16,
            device=self.device
        )

    def allocate(self, num_blocks_needed):
        """Allocate blocks for a request"""
        if len(self.free_blocks) < num_blocks_needed:
            raise OutOfMemoryError("Not enough free blocks")

        # Get free blocks
        allocated = []
        for _ in range(num_blocks_needed):
            block_id = self.free_blocks.pop()
            allocated.append(block_id)

        return allocated

    def free(self, block_ids):
        """Free blocks back to pool"""
        for block_id in block_ids:
            self.free_blocks.add(block_id)

    def can_allocate(self, num_blocks):
        """Check if allocation is possible"""
        return len(self.free_blocks) >= num_blocks

    def get_utilization(self):
        """Current memory utilization"""
        total = len(self.blocks)
        used = total - len(self.free_blocks)
        return used / total
```

<a name="pagedattention"></a>
## 5. PagedAttention Deep Dive

PagedAttention is the CUDA kernel that makes block-based KV cache efficient.

### 5.1 Standard Attention

```python
def standard_attention(query, key, value):
    """
    Standard attention (contiguous KV cache)

    query: [batch_size, num_heads, head_dim]
    key:   [batch_size, num_heads, seq_len, head_dim]
    value: [batch_size, num_heads, seq_len, head_dim]
    """
    # Attention scores
    scores = torch.matmul(
        query.unsqueeze(2),  # [B, H, 1, D]
        key.transpose(-2, -1)  # [B, H, D, S]
    )  # [B, H, 1, S]

    # Scale
    scores = scores / math.sqrt(head_dim)

    # Softmax
    attn_weights = torch.softmax(scores, dim=-1)

    # Apply to values
    output = torch.matmul(
        attn_weights,  # [B, H, 1, S]
        value  # [B, H, S, D]
    )  # [B, H, 1, D]

    return output.squeeze(2)
```

### 5.2 PagedAttention

```python
def paged_attention(query, block_tables, block_size):
    """
    PagedAttention: Attention over non-contiguous blocks

    query: [num_queries, num_heads, head_dim]
    block_tables: [num_queries, max_num_blocks] - maps logical to physical blocks
    block_size: tokens per block

    Returns: [num_queries, num_heads, head_dim]
    """
    # This is implemented in custom CUDA kernel
    # Simplified Python pseudocode:

    outputs = []

    for i in range(num_queries):
        query_i = query[i]  # [num_heads, head_dim]
        blocks_i = block_tables[i]  # [max_num_blocks]

        # Accumulate attention over blocks
        attn_output = torch.zeros_like(query_i)
        softmax_denominator = 0

        for block_id in blocks_i:
            if block_id == -1:  # Empty block
                break

            # Load KV from physical block
            keys_block = load_keys_from_block(block_id)  # [block_size, num_heads, head_dim]
            values_block = load_values_from_block(block_id)

            # Compute attention for this block
            scores_block = torch.matmul(
                query_i.unsqueeze(1),  # [num_heads, 1, head_dim]
                keys_block.transpose(-2, -1)  # [num_heads, head_dim, block_size]
            ) / math.sqrt(head_dim)  # [num_heads, 1, block_size]

            # Exponential (for softmax across blocks)
            exp_scores = torch.exp(scores_block)

            # Accumulate weighted values
            attn_output += torch.matmul(
                exp_scores,  # [num_heads, 1, block_size]
                values_block  # [num_heads, block_size, head_dim]
            ).squeeze(1)

            softmax_denominator += exp_scores.sum(dim=-1)

        # Normalize
        attn_output /= softmax_denominator.unsqueeze(-1)

        outputs.append(attn_output)

    return torch.stack(outputs)
```

**Key Insight**: PagedAttention computes attention correctly even though KV cache is fragmented across non-contiguous blocks.

### 5.3 Performance Optimizations

vLLM's PagedAttention kernel includes:

1. **Block-level Parallelism**: Each thread block handles one attention head
2. **Warp-level Softmax**: Efficient softmax across warps
3. **Shared Memory**: Cache frequently accessed blocks
4. **Coalesced Memory Access**: Optimize block reads
5. **Kernel Fusion**: Combine QKV projection with attention

<a name="scheduling"></a>
## 6. Request Scheduling Algorithms

### 6.1 First-Come-First-Served (FCFS)

```python
class FCFSScheduler:
    """
    Simplest scheduler: Process requests in arrival order
    """
    def __init__(self):
        self.queue = deque()

    def add_request(self, request):
        self.queue.append(request)

    def get_next_batch(self, max_batch_size, available_memory):
        batch = []

        while len(batch) < max_batch_size and self.queue:
            request = self.queue[0]

            if can_fit(request, available_memory):
                self.queue.popleft()
                batch.append(request)
            else:
                break  # Can't fit, stop

        return batch
```

**Pros**: Simple, fair
**Cons**: Long requests block short ones (head-of-line blocking)

### 6.2 Shortest-Job-First (SJF)

```python
class SJFScheduler:
    """
    Schedule shortest requests first for better average latency
    """
    def __init__(self):
        self.queue = []  # Priority queue

    def add_request(self, request):
        # Estimate request length
        estimated_length = estimate_output_length(request)
        heapq.heappush(self.queue, (estimated_length, request))

    def get_next_batch(self, max_batch_size, available_memory):
        batch = []
        temp_queue = []

        while len(batch) < max_batch_size and self.queue:
            _, request = heapq.heappop(self.queue)

            if can_fit(request, available_memory):
                batch.append(request)
            else:
                temp_queue.append(request)

        # Re-add requests that didn't fit
        for request in temp_queue:
            heapq.heappush(self.queue, (estimate_output_length(request), request))

        return batch
```

**Pros**: Lower average latency
**Cons**: Long requests may starve, difficult to estimate length

### 6.3 Priority-Based Scheduling

```python
class PriorityScheduler:
    """
    Schedule based on request priority

    Priority factors:
    - User tier (premium vs free)
    - Request type (interactive vs batch)
    - Waiting time (prevent starvation)
    """
    def __init__(self):
        self.queues = {
            'high': deque(),
            'medium': deque(),
            'low': deque()
        }

    def add_request(self, request):
        priority = self.compute_priority(request)
        self.queues[priority].append(request)

    def compute_priority(self, request):
        score = 0

        # User tier
        score += request.user_tier * 10  # premium = 2, free = 1

        # Request type
        if request.interactive:
            score += 5

        # Waiting time (age)
        score += request.waiting_time / 1000  # Prevent starvation

        # Map to priority level
        if score > 20:
            return 'high'
        elif score > 10:
            return 'medium'
        else:
            return 'low'

    def get_next_batch(self, max_batch_size, available_memory):
        batch = []

        # Try high priority first, then medium, then low
        for priority in ['high', 'medium', 'low']:
            queue = self.queues[priority]

            while len(batch) < max_batch_size and queue:
                request = queue.popleft()

                if can_fit(request, available_memory):
                    batch.append(request)
                else:
                    queue.appendleft(request)  # Put back
                    break

        return batch
```

<a name="memory-pool"></a>
## 7. Memory Pool Management

### 7.1 Memory Pooling Strategy

```python
class MemoryPool:
    """
    Manage GPU memory pool for KV cache blocks
    """
    def __init__(self, total_memory_gb, block_size=16):
        self.block_size = block_size

        # Calculate number of blocks
        bytes_per_block = (
            2 *  # K and V
            num_layers *
            block_size *
            num_heads *
            head_dim *
            2  # FP16 = 2 bytes
        )

        total_bytes = total_memory_gb * 1024**3
        self.num_blocks = int(total_bytes * 0.9 / bytes_per_block)  # 90% utilization

        # Initialize blocks
        self.free_blocks = set(range(self.num_blocks))
        self.block_usage = {}  # block_id -> request_id

    def allocate_for_request(self, request_id, num_blocks):
        """Allocate blocks for a request"""
        if num_blocks > len(self.free_blocks):
            raise OutOfMemoryError

        allocated = []
        for _ in range(num_blocks):
            block_id = self.free_blocks.pop()
            self.block_usage[block_id] = request_id
            allocated.append(block_id)

        return allocated

    def free_request(self, request_id):
        """Free all blocks for a request"""
        blocks_to_free = [
            bid for bid, rid in self.block_usage.items()
            if rid == request_id
        ]

        for block_id in blocks_to_free:
            self.free_blocks.add(block_id)
            del self.block_usage[block_id]

    def get_free_memory_ratio(self):
        """Fraction of free memory"""
        return len(self.free_blocks) / self.num_blocks
```

<a name="preemption"></a>
## 8. Preemption and Swapping

When memory is exhausted, preempt low-priority requests.

### 8.1 Preemption Policy

```python
class PreemptionManager:
    """
    Decide which requests to preempt when out of memory
    """
    def __init__(self, scheduler, memory_pool):
        self.scheduler = scheduler
        self.memory_pool = memory_pool

    def select_requests_to_preempt(self, blocks_needed):
        """
        Select requests to preempt to free blocks_needed blocks

        Strategy: Preempt lowest priority requests
        """
        running_requests = self.scheduler.running_requests

        # Sort by priority (ascending)
        sorted_requests = sorted(
            running_requests,
            key=lambda r: (r.priority, -r.num_tokens_generated)
        )

        to_preempt = []
        blocks_freed = 0

        for request in sorted_requests:
            blocks_freed += request.num_blocks
            to_preempt.append(request)

            if blocks_freed >= blocks_needed:
                break

        return to_preempt

    def preempt_request(self, request):
        """
        Preempt a request: Save state and free memory
        """
        # Option 1: Swap to CPU (if CPU memory available)
        if self.can_swap_to_cpu():
            request.kv_cache_cpu = request.kv_cache.to('cpu')
            request.state = 'swapped'

        # Option 2: Recompute (discard KV cache)
        else:
            request.state = 'preempted'
            # Will need to recompute from prompt when resumed

        # Free GPU memory
        self.memory_pool.free_request(request.id)
        self.scheduler.running_requests.remove(request)
        self.scheduler.waiting_queue.appendleft(request)

    def resume_request(self, request):
        """Resume a preempted request"""
        if request.state == 'swapped':
            # Swap back from CPU
            request.kv_cache = request.kv_cache_cpu.to('cuda')
            del request.kv_cache_cpu

        elif request.state == 'preempted':
            # Recompute: Run prefill again
            request.reset_to_prompt()

        request.state = 'running'
        self.scheduler.running_requests.append(request)
```

<a name="performance"></a>
## 9. Performance Optimization

### 9.1 Batch Size Tuning

```python
def find_optimal_batch_size(model, memory_pool):
    """
    Binary search for optimal batch size

    Maximize batch size while staying under memory limit
    """
    low, high = 1, 256
    optimal = 1

    while low <= high:
        mid = (low + high) // 2

        # Try batch size
        try:
            test_batch_size(model, mid, memory_pool)
            optimal = mid
            low = mid + 1  # Try larger
        except OutOfMemoryError:
            high = mid - 1  # Try smaller

    return optimal
```

### 9.2 Adaptive Block Size

```python
class AdaptiveBlockManager:
    """
    Dynamically adjust block size based on workload
    """
    def __init__(self, initial_block_size=16):
        self.block_size = initial_block_size

    def analyze_workload(self, completed_requests):
        """Analyze recent requests to optimize block size"""
        avg_length = np.mean([r.num_tokens for r in completed_requests])

        # If avg length is much larger than block size, increase
        if avg_length > self.block_size * 4:
            self.block_size = min(32, self.block_size * 2)

        # If avg length close to block size, decrease to reduce waste
        elif avg_length < self.block_size * 0.5:
            self.block_size = max(4, self.block_size // 2)
```

<a name="implementation"></a>
## 10. Implementation Patterns

### Complete Continuous Batching System

```python
class ContinuousBatchingEngine:
    """
    Complete implementation of continuous batching for LLM serving
    """
    def __init__(self, model, config):
        self.model = model
        self.config = config

        # Components
        self.scheduler = PriorityScheduler()
        self.memory_pool = BlockMemoryPool(
            num_blocks=config.max_num_blocks,
            block_size=config.block_size
        )
        self.preemption_manager = PreemptionManager(
            self.scheduler,
            self.memory_pool
        )

        # Metrics
        self.metrics = {
            'throughput': [],
            'latency': [],
            'batch_sizes': [],
            'memory_utilization': []
        }

    async def serve(self):
        """Main serving loop"""
        while True:
            # 1. Process new requests
            while not self.scheduler.waiting_queue.empty():
                if self.should_admit_request():
                    request = self.scheduler.waiting_queue.popleft()
                    self.admit_request(request)
                else:
                    break

            # 2. Generate next token for running requests
            if self.scheduler.running_requests:
                await self.generation_step()

            # 3. Update metrics
            self.update_metrics()

            # 4. Handle preemption if needed
            if self.memory_pool.get_free_memory_ratio() < 0.1:
                self.handle_low_memory()

    async def generation_step(self):
        """Single step of token generation"""
        # Prepare batch
        batch_input_ids = [
            r.next_token_id
            for r in self.scheduler.running_requests
        ]
        batch_block_tables = [
            r.block_table
            for r in self.scheduler.running_requests
        ]

        # Model forward pass
        with torch.no_grad():
            logits = self.model(
                input_ids=batch_input_ids,
                block_tables=batch_block_tables
            )

        # Sample and update
        for request, logit in zip(self.scheduler.running_requests, logits):
            next_token = sample_token(logit, request.sampling_params)
            request.append_token(next_token)

            # Allocate more blocks if needed
            if request.needs_more_blocks():
                new_blocks = self.memory_pool.allocate(1)
                request.add_blocks(new_blocks)

        # Remove finished
        finished = [r for r in self.scheduler.running_requests if r.is_finished()]
        for request in finished:
            self.finish_request(request)

    def should_admit_request(self):
        """Admission control"""
        # Check batch size
        if len(self.scheduler.running_requests) >= self.config.max_batch_size:
            return False

        # Check memory
        if self.memory_pool.get_free_memory_ratio() < 0.2:
            return False

        return True

    def handle_low_memory(self):
        """Handle memory pressure"""
        # Preempt lowest priority requests
        to_preempt = self.preemption_manager.select_requests_to_preempt(
            blocks_needed=10
        )

        for request in to_preempt:
            self.preemption_manager.preempt_request(request)
```

## Summary

Continuous batching with intelligent KV cache management:

- **Continuous Batching**: Dynamic batch adjustment (2-10x throughput improvement)
- **PagedAttention**: Block-based KV cache (80-95% memory utilization)
- **Scheduling**: FCFS, SJF, priority-based algorithms
- **Memory Management**: Block pooling, allocation strategies
- **Preemption**: Swap/recompute for memory pressure
- **Optimization**: Adaptive batch size, block size tuning

These techniques enable production LLM serving at scale!

## Next Steps

1. Complete Lab 04: Implement continuous batching
2. Review all module content
3. Take the module assessment quiz

---

**Lecture Duration**: 6 hours
**Difficulty**: Advanced
