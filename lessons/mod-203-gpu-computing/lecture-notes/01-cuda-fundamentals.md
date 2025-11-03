# Lecture 01: CUDA Fundamentals

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement custom CUDA kernels for ML workload optimization when framework-provided operations are insufficient
- Architect memory access patterns that maximize coalescing efficiency and minimize bank conflicts for optimal GPU memory bandwidth utilization
- Implement thread hierarchy strategies (grids, blocks, warps) that balance occupancy, register usage, and shared memory constraints for specific workloads
- Configure and optimize kernel launch parameters using occupancy calculators to achieve maximum SM utilization for different kernel characteristics
- Integrate custom CUDA operations into PyTorch and TensorFlow training pipelines using framework extension APIs
- Evaluate performance trade-offs between CUDA kernel optimizations (occupancy vs register pressure, shared memory vs global memory)
- Implement synchronization primitives and atomic operations correctly to avoid race conditions in multi-threaded GPU kernels
- Design CUDA-accelerated data preprocessing and augmentation pipelines to eliminate CPU-GPU transfer bottlenecks in training workflows

## Table of Contents
1. [Introduction to CUDA](#introduction-to-cuda)
2. [CUDA Programming Model](#cuda-programming-model)
3. [Threads, Blocks, and Grids](#threads-blocks-and-grids)
4. [Memory Hierarchy](#memory-hierarchy)
5. [Writing Your First CUDA Kernel](#writing-your-first-cuda-kernel)
6. [CUDA C++ Programming](#cuda-c-programming)
7. [CUDA Streams and Concurrency](#cuda-streams-and-concurrency)
8. [Error Handling and Debugging](#error-handling-and-debugging)
9. [Best Practices](#best-practices)

## Introduction to CUDA

CUDA (Compute Unified Device Architecture) is NVIDIA's parallel computing platform and programming model that enables developers to use GPUs for general-purpose computing. Understanding CUDA is essential for AI infrastructure engineers who need to optimize ML workloads, write custom operations, and troubleshoot GPU performance issues.

### Why CUDA for AI Infrastructure?

1. **Performance Optimization**: Direct control over GPU execution for maximum performance
2. **Custom Operations**: Implement specialized ML operations not available in frameworks
3. **Debugging**: Understanding CUDA helps diagnose GPU performance issues
4. **Framework Integration**: PyTorch and TensorFlow use CUDA under the hood
5. **Hardware Utilization**: Maximize GPU efficiency and throughput

### CUDA Architecture Overview

CUDA provides a bridge between high-level application code and GPU hardware:

```
Application Layer (PyTorch/TensorFlow)
          ↓
CUDA Libraries (cuDNN, cuBLAS)
          ↓
CUDA Runtime API
          ↓
CUDA Driver API
          ↓
GPU Hardware
```

### CUDA Toolkit Components

The CUDA Toolkit includes:

- **nvcc**: NVIDIA CUDA Compiler
- **cuda-gdb**: CUDA debugger
- **CUDA Runtime**: High-level API for GPU programming
- **CUDA Driver**: Low-level API for direct hardware control
- **Libraries**: cuBLAS, cuDNN, cuFFT, cuSPARSE, etc.
- **Profilers**: Nsight Systems, Nsight Compute
- **Samples**: Example CUDA programs

### Installation and Setup

```bash
# Check CUDA installation
nvcc --version
nvidia-smi

# Verify CUDA samples
cd /usr/local/cuda/samples/1_Utilities/deviceQuery
make
./deviceQuery

# Expected output shows GPU properties:
# - CUDA Capability
# - Memory size
# - Number of SMs
# - Clock speeds
```

## CUDA Programming Model

The CUDA programming model is based on heterogeneous computing with CPUs (hosts) and GPUs (devices) working together.

### Host and Device

- **Host**: The CPU and its memory (RAM)
- **Device**: The GPU and its memory (VRAM)
- **Kernel**: A function that runs on the GPU
- **Thread**: The smallest unit of execution on GPU

### Execution Flow

A typical CUDA program follows this pattern:

1. Allocate memory on the host
2. Allocate memory on the device
3. Copy data from host to device
4. Launch kernel on device
5. Copy results from device to host
6. Free device and host memory

### CUDA Function Types

CUDA defines three function type qualifiers:

```cpp
// Runs on host, called from host (regular C++ function)
void hostFunction() { }

// Runs on device, called from device (kernel helper)
__device__ void deviceFunction() { }

// Runs on device, called from host (kernel entry point)
__global__ void kernelFunction() { }

// Runs on both host and device
__host__ __device__ void bothFunction() { }
```

### Simple CUDA Example

Here's a complete example that adds two arrays:

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

// Kernel definition: runs on GPU
__global__ void vectorAdd(const float* A, const float* B, float* C, int N) {
    // Calculate global thread ID
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    // Boundary check
    if (idx < N) {
        C[idx] = A[idx] + B[idx];
    }
}

int main() {
    int N = 1000000;  // 1 million elements
    size_t size = N * sizeof(float);

    // 1. Allocate host memory
    float *h_A = (float*)malloc(size);
    float *h_B = (float*)malloc(size);
    float *h_C = (float*)malloc(size);

    // Initialize host arrays
    for (int i = 0; i < N; i++) {
        h_A[i] = i;
        h_B[i] = i * 2;
    }

    // 2. Allocate device memory
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, size);
    cudaMalloc(&d_B, size);
    cudaMalloc(&d_C, size);

    // 3. Copy data from host to device
    cudaMemcpy(d_A, h_A, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, size, cudaMemcpyHostToDevice);

    // 4. Launch kernel
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;
    vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);

    // 5. Copy result back to host
    cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);

    // Verify result
    for (int i = 0; i < 10; i++) {
        printf("C[%d] = %.2f\n", i, h_C[i]);
    }

    // 6. Free memory
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    free(h_A);
    free(h_B);
    free(h_C);

    return 0;
}
```

### Compilation

```bash
# Compile CUDA program
nvcc -o vectorAdd vectorAdd.cu

# Run
./vectorAdd
```

## Threads, Blocks, and Grids

CUDA's execution model is hierarchical: threads are organized into blocks, and blocks are organized into grids.

### Thread Hierarchy

```
Grid (all blocks)
├── Block (0,0)
│   ├── Thread (0,0)
│   ├── Thread (0,1)
│   └── Thread (0,2)
├── Block (0,1)
│   ├── Thread (0,0)
│   ├── Thread (0,1)
│   └── Thread (0,2)
└── Block (1,0)
    ├── Thread (0,0)
    ├── Thread (0,1)
    └── Thread (0,2)
```

### Built-in Variables

Inside a kernel, you have access to:

- **threadIdx**: Thread index within its block (x, y, z)
- **blockIdx**: Block index within the grid (x, y, z)
- **blockDim**: Block dimensions (x, y, z)
- **gridDim**: Grid dimensions (x, y, z)

### Calculating Global Thread ID

For 1D grids and blocks:
```cpp
int idx = blockDim.x * blockIdx.x + threadIdx.x;
```

For 2D grids and blocks:
```cpp
int x = blockDim.x * blockIdx.x + threadIdx.x;
int y = blockDim.y * blockIdx.y + threadIdx.y;
int idx = y * width + x;  // Convert to linear index
```

For 3D grids and blocks:
```cpp
int x = blockDim.x * blockIdx.x + threadIdx.x;
int y = blockDim.y * blockIdx.y + threadIdx.y;
int z = blockDim.z * blockIdx.z + threadIdx.z;
int idx = z * (width * height) + y * width + x;
```

### Choosing Block and Grid Dimensions

**Block Size Considerations:**
- Multiple of 32 (warp size) for efficiency
- Typically 128, 256, or 512 threads per block
- Maximum 1024 threads per block (hardware limit)
- Should be tuned based on register and shared memory usage

**Grid Size Calculation:**
```cpp
int threadsPerBlock = 256;
int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;  // Ceiling division
```

### Example: 2D Matrix Addition

```cpp
__global__ void matrixAdd(float* A, float* B, float* C, int width, int height) {
    // Calculate 2D position
    int col = blockDim.x * blockIdx.x + threadIdx.x;
    int row = blockDim.y * blockIdx.y + threadIdx.y;

    // Boundary check
    if (col < width && row < height) {
        int idx = row * width + col;
        C[idx] = A[idx] + B[idx];
    }
}

// Launch configuration
dim3 threadsPerBlock(16, 16);  // 256 threads per block
dim3 blocksPerGrid(
    (width + threadsPerBlock.x - 1) / threadsPerBlock.x,
    (height + threadsPerBlock.y - 1) / threadsPerBlock.y
);
matrixAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, width, height);
```

### Warps and Warp Execution

A **warp** is a group of 32 threads that execute in lockstep (SIMT - Single Instruction, Multiple Threads).

Key warp concepts:
- Threads 0-31 form warp 0, threads 32-63 form warp 1, etc.
- All threads in a warp execute the same instruction
- **Warp divergence** occurs when threads take different code paths (if/else)
- Divergence causes serialization and reduced performance

Example of warp divergence:
```cpp
__global__ void divergentKernel(int* data) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    // Bad: causes warp divergence if idx is not uniform
    if (idx % 2 == 0) {
        data[idx] = expensiveComputation1(idx);  // Even threads
    } else {
        data[idx] = expensiveComputation2(idx);  // Odd threads
    }
    // Warp executes both branches, masking inactive threads
}
```

Avoiding divergence when possible:
```cpp
__global__ void convergentKernel(int* data) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    // Better: all threads in a warp likely take same path
    if (idx < 1000000) {
        data[idx] = computation(idx);
    }
}
```

## Memory Hierarchy

Understanding GPU memory is critical for performance optimization.

### Memory Types

1. **Global Memory**
   - Largest memory space (GBs)
   - Slowest access (~400-800 cycles latency)
   - Accessible by all threads
   - Allocated with `cudaMalloc()`
   - Persists for entire application

2. **Shared Memory**
   - Per-block memory (48-164 KB per SM)
   - Fast access (~5-10 cycles latency)
   - Shared among threads in the same block
   - Declared with `__shared__` qualifier
   - Useful for thread cooperation

3. **Registers**
   - Fastest memory
   - Private to each thread
   - Limited (typically 64K 32-bit registers per SM)
   - Automatic variables stored in registers

4. **Constant Memory**
   - Read-only memory (64 KB)
   - Cached for fast access
   - Broadcast reads are efficient
   - Declared with `__constant__` qualifier

5. **Texture Memory**
   - Read-only, cached memory
   - Optimized for 2D spatial locality
   - Hardware interpolation support

6. **Local Memory**
   - Actually in global memory
   - Used for register spills and large arrays
   - Should be avoided when possible

### Memory Hierarchy Diagram

```
Speed   Size    Scope
Fast    Small   Thread-local
  ↓       ↓        ↓
Registers (32-bit each)
Local Memory (spills)
  ↓
Shared Memory (per block)
  ↓
L1 Cache
  ↓
L2 Cache
  ↓
Global Memory (DRAM)
Slow    Large   All threads
```

### Example: Using Shared Memory

Shared memory enables thread cooperation and reduces global memory accesses:

```cpp
__global__ void matrixMultiplyShared(float* A, float* B, float* C, int N) {
    // Shared memory for tile of A and B
    __shared__ float tileA[16][16];
    __shared__ float tileB[16][16];

    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    float sum = 0.0f;

    // Loop over tiles
    for (int t = 0; t < (N + 15) / 16; t++) {
        // Load tile into shared memory
        if (row < N && (t * 16 + threadIdx.x) < N) {
            tileA[threadIdx.y][threadIdx.x] = A[row * N + t * 16 + threadIdx.x];
        } else {
            tileA[threadIdx.y][threadIdx.x] = 0.0f;
        }

        if (col < N && (t * 16 + threadIdx.y) < N) {
            tileB[threadIdx.y][threadIdx.x] = B[(t * 16 + threadIdx.y) * N + col];
        } else {
            tileB[threadIdx.y][threadIdx.x] = 0.0f;
        }

        // Synchronize to ensure tile is loaded
        __syncthreads();

        // Compute partial result
        for (int k = 0; k < 16; k++) {
            sum += tileA[threadIdx.y][k] * tileB[k][threadIdx.x];
        }

        // Synchronize before loading next tile
        __syncthreads();
    }

    if (row < N && col < N) {
        C[row * N + col] = sum;
    }
}
```

### Memory Access Patterns

**Coalesced Access** (Good):
```cpp
// Threads in a warp access consecutive memory locations
__global__ void coalescedAccess(float* data) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    float value = data[idx];  // Coalesced: threads 0-31 access data[0-31]
}
```

**Strided Access** (Bad):
```cpp
// Threads in a warp access memory with large strides
__global__ void stridedAccess(float* data, int stride) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    float value = data[idx * stride];  // Strided: poor memory bandwidth
}
```

### Synchronization

**`__syncthreads()`**: Synchronizes all threads within a block
- Must be called by all threads in the block
- Cannot be in divergent code paths
- Used before/after shared memory access

```cpp
__global__ void synchronizationExample(float* data) {
    __shared__ float shared[256];

    int idx = threadIdx.x;

    // Load data into shared memory
    shared[idx] = data[idx];

    // Wait for all threads to load
    __syncthreads();

    // Now all threads can safely access shared[]
    float result = shared[255 - idx];

    __syncthreads();  // Before next phase
}
```

## Writing Your First CUDA Kernel

Let's write a CUDA kernel for a common ML operation: ReLU activation.

### ReLU Activation Function

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

// ReLU kernel: f(x) = max(0, x)
__global__ void reluKernel(const float* input, float* output, int N) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    if (idx < N) {
        output[idx] = fmaxf(0.0f, input[idx]);  // fmaxf is GPU intrinsic
    }
}

// Host function to launch ReLU kernel
void reluForward(const float* d_input, float* d_output, int N) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    reluKernel<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, N);

    // Check for kernel launch errors
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("ReLU kernel launch error: %s\n", cudaGetErrorString(err));
    }
}

// TODO: Implement ReLU backward pass (gradient computation)
__global__ void reluBackwardKernel(const float* input, const float* grad_output,
                                    float* grad_input, int N) {
    // TODO: Implement backward pass
    // grad_input[i] = input[i] > 0 ? grad_output[i] : 0
}
```

### Softmax Activation (More Complex)

```cpp
// TODO: Implement softmax kernel
// Softmax: softmax(x_i) = exp(x_i) / sum(exp(x_j))
// Challenge: Requires reduction and normalization

__global__ void softmaxKernel(const float* input, float* output, int batch_size, int dim) {
    // Each block processes one sample in the batch
    int batch_idx = blockIdx.x;

    if (batch_idx >= batch_size) return;

    const float* input_row = input + batch_idx * dim;
    float* output_row = output + batch_idx * dim;

    // TODO: Step 1 - Find max value (for numerical stability)
    // Use shared memory reduction

    // TODO: Step 2 - Compute exp(x - max) and sum
    // Use shared memory for partial sums

    // TODO: Step 3 - Normalize by sum
}
```

### Matrix Multiplication (Fundamental)

```cpp
// Naive matrix multiplication: C = A * B
// A: M x K, B: K x N, C: M x N
__global__ void matmulNaive(const float* A, const float* B, float* C,
                             int M, int K, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < K; k++) {
            sum += A[row * K + k] * B[k * N + col];
        }
        C[row * N + col] = sum;
    }
}

// TODO: Implement tiled matrix multiplication using shared memory
// This reduces global memory accesses from 2*K to 2*K/TILE_SIZE per element
__global__ void matmulTiled(const float* A, const float* B, float* C,
                             int M, int K, int N) {
    // TODO: Use shared memory tiles
    // TODO: Load tiles cooperatively
    // TODO: Compute partial products
    // TODO: Accumulate results
}
```

## CUDA C++ Programming

CUDA supports modern C++ features and provides additional GPU-specific extensions.

### Templates and Generics

```cpp
// Template kernel works with any numeric type
template<typename T>
__global__ void vectorAddTemplate(const T* A, const T* B, T* C, int N) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < N) {
        C[idx] = A[idx] + B[idx];
    }
}

// Launch with different types
vectorAddTemplate<float><<<blocks, threads>>>(d_A_float, d_B_float, d_C_float, N);
vectorAddTemplate<double><<<blocks, threads>>>(d_A_double, d_B_double, d_C_double, N);
vectorAddTemplate<int><<<blocks, threads>>>(d_A_int, d_B_int, d_C_int, N);
```

### Device Functions

```cpp
// Helper function callable from kernel
__device__ float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

__device__ float sigmoidGradient(float x) {
    float s = sigmoid(x);
    return s * (1.0f - s);
}

__global__ void sigmoidActivation(const float* input, float* output, int N) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < N) {
        output[idx] = sigmoid(input[idx]);  // Call device function
    }
}
```

### Inline Functions

```cpp
// Force inlining for performance
__forceinline__ __device__ float fastAdd(float a, float b) {
    return a + b;
}
```

### Atomics

Atomic operations for safe concurrent updates:

```cpp
__global__ void histogramKernel(const int* data, int* histogram, int N, int num_bins) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    if (idx < N) {
        int bin = data[idx];
        if (bin >= 0 && bin < num_bins) {
            atomicAdd(&histogram[bin], 1);  // Thread-safe increment
        }
    }
}

// Available atomic operations:
// atomicAdd, atomicSub, atomicExch, atomicMin, atomicMax
// atomicInc, atomicDec, atomicCAS (compare-and-swap)
// atomicAnd, atomicOr, atomicXor
```

### Warp-level Primitives

Modern CUDA provides warp-level operations for efficiency:

```cpp
#include <cuda/std/utility>

__global__ void warpReduction(const float* input, float* output, int N) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    int lane = threadIdx.x % 32;  // Lane within warp

    float value = (idx < N) ? input[idx] : 0.0f;

    // Warp-level reduction using shuffle
    for (int offset = 16; offset > 0; offset /= 2) {
        value += __shfl_down_sync(0xffffffff, value, offset);
    }

    // First thread in warp writes result
    if (lane == 0) {
        atomicAdd(output, value);
    }
}

// Other warp primitives:
// __shfl_sync() - shuffle data between threads
// __shfl_up_sync() - shuffle up
// __shfl_down_sync() - shuffle down
// __shfl_xor_sync() - shuffle with XOR
// __ballot_sync() - vote across warp
// __any_sync() - returns true if any thread's predicate is true
// __all_sync() - returns true if all threads' predicates are true
```

## CUDA Streams and Concurrency

CUDA streams enable concurrent execution of kernels and memory transfers.

### What is a CUDA Stream?

A stream is a sequence of operations that execute in order. Operations in different streams can execute concurrently.

### Default Stream vs. Non-default Streams

```cpp
// Default stream (stream 0) - synchronizes with all streams
kernel1<<<blocks, threads>>>(args);  // Uses default stream

// Create custom streams
cudaStream_t stream1, stream2;
cudaStreamCreate(&stream1);
cudaStreamCreate(&stream2);

// Launch kernels in different streams
kernel1<<<blocks, threads, 0, stream1>>>(args1);
kernel2<<<blocks, threads, 0, stream2>>>(args2);  // Can run concurrently

// Cleanup
cudaStreamDestroy(stream1);
cudaStreamDestroy(stream2);
```

### Overlapping Computation and Communication

```cpp
void pipelinedExecution(float* h_data, float* d_data, int N, int num_streams) {
    cudaStream_t streams[num_streams];
    for (int i = 0; i < num_streams; i++) {
        cudaStreamCreate(&streams[i]);
    }

    int chunk_size = N / num_streams;

    for (int i = 0; i < num_streams; i++) {
        int offset = i * chunk_size;

        // Each stream: copy H2D -> compute -> copy D2H
        cudaMemcpyAsync(&d_data[offset], &h_data[offset],
                       chunk_size * sizeof(float),
                       cudaMemcpyHostToDevice, streams[i]);

        processKernel<<<blocks, threads, 0, streams[i]>>>(&d_data[offset], chunk_size);

        cudaMemcpyAsync(&h_data[offset], &d_data[offset],
                       chunk_size * sizeof(float),
                       cudaMemcpyDeviceToHost, streams[i]);
    }

    // Wait for all streams to complete
    cudaDeviceSynchronize();

    for (int i = 0; i < num_streams; i++) {
        cudaStreamDestroy(streams[i]);
    }
}
```

### Stream Synchronization

```cpp
// Wait for specific stream
cudaStreamSynchronize(stream1);

// Wait for all streams
cudaDeviceSynchronize();

// Check if stream is complete (non-blocking)
cudaError_t err = cudaStreamQuery(stream1);
if (err == cudaSuccess) {
    // Stream is idle
} else if (err == cudaErrorNotReady) {
    // Stream still working
}
```

### Events for Timing

```cpp
cudaEvent_t start, stop;
cudaEventCreate(&start);
cudaEventCreate(&stop);

// Record start event
cudaEventRecord(start);

// Execute kernel
kernel<<<blocks, threads>>>(args);

// Record stop event
cudaEventRecord(stop);

// Wait for stop event
cudaEventSynchronize(stop);

// Calculate elapsed time
float milliseconds = 0;
cudaEventElapsedTime(&milliseconds, start, stop);
printf("Kernel execution time: %.3f ms\n", milliseconds);

// Cleanup
cudaEventDestroy(start);
cudaEventDestroy(stop);
```

## Error Handling and Debugging

Robust error handling is essential for production CUDA code.

### Error Checking Macro

```cpp
#define CUDA_CHECK(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            fprintf(stderr, "CUDA error at %s:%d - %s\n", \
                    __FILE__, __LINE__, cudaGetErrorString(err)); \
            exit(EXIT_FAILURE); \
        } \
    } while(0)

// Usage
CUDA_CHECK(cudaMalloc(&d_data, size));
CUDA_CHECK(cudaMemcpy(d_data, h_data, size, cudaMemcpyHostToDevice));
```

### Kernel Launch Error Checking

```cpp
kernel<<<blocks, threads>>>(args);

// Check for launch errors
CUDA_CHECK(cudaGetLastError());

// Check for execution errors
CUDA_CHECK(cudaDeviceSynchronize());
```

### Common Errors

1. **Invalid Configuration**: Too many threads per block
2. **Out of Memory**: cudaMalloc fails
3. **Invalid Memory Access**: Accessing out-of-bounds memory
4. **Launch Timeout**: Kernel runs too long (display driver watchdog)
5. **Invalid Value**: Passing invalid parameters

### Debugging with printf

```cpp
__global__ void debugKernel(int* data, int N) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    // Print from first thread only to reduce output
    if (idx == 0) {
        printf("Kernel launched with %d blocks, %d threads\n",
               gridDim.x, blockDim.x);
    }

    if (idx < N) {
        // Debug specific thread
        if (idx == 100) {
            printf("Thread %d: data = %d\n", idx, data[idx]);
        }

        data[idx] = idx;
    }
}
```

### Debugging with cuda-gdb

```bash
# Compile with debug symbols
nvcc -g -G -o program program.cu

# Run with debugger
cuda-gdb ./program

# cuda-gdb commands
(cuda-gdb) break kernel_name  # Set breakpoint
(cuda-gdb) run                # Run program
(cuda-gdb) cuda thread        # Show current CUDA thread
(cuda-gdb) cuda block         # Show current block
(cuda-gdb) info cuda threads  # List all threads
(cuda-gdb) print variable     # Print variable value
```

### Compute Sanitizer

```bash
# Check for memory errors
compute-sanitizer --tool memcheck ./program

# Check for race conditions
compute-sanitizer --tool racecheck ./program

# Check for initialization errors
compute-sanitizer --tool initcheck ./program

# Check for synchronization errors
compute-sanitizer --tool synccheck ./program
```

## Best Practices

### Performance Optimization

1. **Maximize Occupancy**: Keep GPU busy with enough threads
2. **Coalesce Memory Access**: Ensure consecutive threads access consecutive memory
3. **Minimize Divergence**: Avoid if/else in warps when possible
4. **Use Shared Memory**: Cache frequently accessed data
5. **Optimize Register Usage**: Reduce register spills to local memory
6. **Stream Concurrency**: Overlap computation and communication

### Code Organization

```cpp
// Header file: kernels.cuh
#ifndef KERNELS_CUH
#define KERNELS_CUH

// Kernel declarations
__global__ void myKernel(float* data, int N);

// Host wrapper functions
void launchMyKernel(float* d_data, int N);

#endif

// Implementation: kernels.cu
#include "kernels.cuh"

__global__ void myKernel(float* data, int N) {
    // Implementation
}

void launchMyKernel(float* d_data, int N) {
    int threads = 256;
    int blocks = (N + threads - 1) / threads;
    myKernel<<<blocks, threads>>>(d_data, N);
    CUDA_CHECK(cudaGetLastError());
}
```

### Memory Management

```cpp
// RAII wrapper for CUDA memory
template<typename T>
class CudaBuffer {
public:
    CudaBuffer(size_t size) : size_(size) {
        CUDA_CHECK(cudaMalloc(&ptr_, size * sizeof(T)));
    }

    ~CudaBuffer() {
        cudaFree(ptr_);
    }

    T* get() { return ptr_; }
    size_t size() const { return size_; }

    // Delete copy constructor and assignment
    CudaBuffer(const CudaBuffer&) = delete;
    CudaBuffer& operator=(const CudaBuffer&) = delete;

private:
    T* ptr_;
    size_t size_;
};

// Usage
CudaBuffer<float> buffer(1000);
kernel<<<blocks, threads>>>(buffer.get(), buffer.size());
// Automatic cleanup when buffer goes out of scope
```

### Pinned Memory for Faster Transfers

```cpp
// Allocate pinned (page-locked) host memory
float* h_data;
CUDA_CHECK(cudaMallocHost(&h_data, size));  // Pinned memory

// Faster H2D and D2H transfers
CUDA_CHECK(cudaMemcpy(d_data, h_data, size, cudaMemcpyHostToDevice));

// Free pinned memory
CUDA_CHECK(cudaFreeHost(h_data));
```

### Unified Memory (Managed Memory)

```cpp
// Allocate unified memory (accessible from CPU and GPU)
float* data;
CUDA_CHECK(cudaMallocManaged(&data, size));

// Use on CPU
for (int i = 0; i < N; i++) {
    data[i] = i;
}

// Use on GPU (automatic migration)
kernel<<<blocks, threads>>>(data, N);
CUDA_CHECK(cudaDeviceSynchronize());

// Use on CPU again
printf("Result: %f\n", data[0]);

CUDA_CHECK(cudaFree(data));
```

## Summary

In this lecture, we covered CUDA fundamentals:

- CUDA programming model: host/device, kernels, threads
- Thread hierarchy: threads, blocks, grids
- Memory hierarchy: global, shared, registers, constant
- Writing CUDA kernels for ML operations
- CUDA C++ features: templates, atomics, warp primitives
- Streams for concurrency and overlap
- Error handling and debugging techniques
- Best practices for performance and code organization

## Next Steps

- **Practice**: Write CUDA kernels for common ML operations (ReLU, Softmax, BatchNorm)
- **Profile**: Use nvprof or Nsight to analyze kernel performance
- **Optimize**: Apply shared memory and coalescing techniques
- **Read**: NVIDIA CUDA Programming Guide
- **Proceed**: Next lecture covers GPU architecture in depth

## Further Reading

- NVIDIA CUDA C Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
- CUDA C Best Practices Guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
- CUDA Samples: /usr/local/cuda/samples/
- "Programming Massively Parallel Processors" by Hwu, Kirk, and Hajj

---

**Next Lecture**: GPU Architecture Deep Dive - Understanding Ampere and Hopper architectures
