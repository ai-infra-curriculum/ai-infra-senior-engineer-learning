# Lecture 05: Model Pruning and Knowledge Distillation

## Learning Objectives

By the end of this lecture, you will be able to:

- Design model compression strategies selecting appropriate techniques (pruning, distillation, low-rank factorization, PEFT) based on target compression ratio and accuracy constraints
- Implement magnitude-based pruning algorithms including gradual pruning schedules and iterative magnitude pruning (Lottery Ticket Hypothesis) achieving 50-90% sparsity
- Architect structured pruning solutions that remove entire channels, filters, or heads for immediate speedup on standard hardware without specialized sparse kernels
- Apply N:M sparsity patterns (2:4 sparsity) to leverage NVIDIA Ampere Tensor Core acceleration achieving 2x speedup with minimal accuracy loss
- Implement knowledge distillation training student models from teacher models using soft targets, temperature scaling, and feature-based distillation for 2-10x model compression
- Configure LoRA (Low-Rank Adaptation) and QLoRA for parameter-efficient fine-tuning achieving 99%+ reduction in trainable parameters while maintaining model quality
- Combine multiple compression techniques (distillation + quantization + pruning) in multi-stage pipelines for maximum compression (10-100x) with controlled accuracy degradation
- Validate compressed models comprehensively measuring accuracy, latency, memory, throughput, and per-class performance before production deployment

## Table of Contents
1. [Introduction to Model Compression](#introduction)
2. [Neural Network Pruning](#pruning)
3. [Structured vs Unstructured Pruning](#structured-vs-unstructured)
4. [Pruning Algorithms](#pruning-algorithms)
5. [Knowledge Distillation](#distillation)
6. [Advanced Distillation Techniques](#advanced-distillation)
7. [Low-Rank Factorization](#low-rank)
8. [Parameter-Efficient Fine-Tuning](#peft)
9. [Combining Compression Techniques](#combining)
10. [Production Considerations](#production)

<a name="introduction"></a>
## 1. Introduction to Model Compression

Model compression reduces model size and computational requirements while maintaining performance. Unlike quantization (reducing precision), compression reduces the number of parameters or operations.

### Compression Techniques Overview

**Pruning**: Remove unnecessary weights or neurons
- Unstructured: Remove individual weights (irregular sparsity)
- Structured: Remove entire channels, filters, or layers
- Typical compression: 50-90% sparsity
- Speedup: Requires sparse hardware/kernels for unstructured

**Knowledge Distillation**: Train small model to mimic large model
- Creates entirely new smaller model
- Student learns from teacher's knowledge
- Typical compression: 2-10x smaller models
- Speedup: Directly proportional to size reduction

**Low-Rank Factorization**: Decompose weight matrices
- Factorize W = U × V where U, V are smaller
- Reduces parameters but maintains structure
- Typical compression: 2-4x
- Immediate speedup without special hardware

**Parameter-Efficient Fine-Tuning (PEFT)**: Add small trainable components
- LoRA, Adapters, Prefix-tuning
- Primarily for fine-tuning, but enables smaller deployed models
- Compression: 99%+ fewer trainable parameters

<a name="pruning"></a>
## 2. Neural Network Pruning

### 2.1 Magnitude-Based Pruning

Simplest and most common pruning method: remove smallest weights.

```python
import torch
import torch.nn as nn

def magnitude_prune(model, sparsity=0.5):
    """
    Prune weights with smallest magnitudes

    Args:
        model: PyTorch model
        sparsity: Fraction of weights to prune (0.5 = 50%)
    """
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            weight = module.weight.data

            # Compute threshold
            threshold = torch.quantile(
                torch.abs(weight.flatten()),
                sparsity
            )

            # Create mask
            mask = torch.abs(weight) > threshold

            # Apply mask
            weight.mul_(mask)

            # Register mask for training
            module.register_buffer(f'{name}_mask', mask)

    return model

# Usage
model = YourModel()
pruned_model = magnitude_prune(model, sparsity=0.7)  # 70% sparsity
```

### 2.2 Gradual Pruning

Prune progressively during training for better accuracy:

```python
class GradualPruner:
    def __init__(self, model, initial_sparsity=0.0, final_sparsity=0.9,
                 start_epoch=0, end_epoch=100, frequency=10):
        self.model = model
        self.initial_sparsity = initial_sparsity
        self.final_sparsity = final_sparsity
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch
        self.frequency = frequency

    def compute_sparsity(self, epoch):
        """Cubic sparsity schedule"""
        if epoch < self.start_epoch:
            return self.initial_sparsity
        if epoch >= self.end_epoch:
            return self.final_sparsity

        progress = (epoch - self.start_epoch) / (self.end_epoch - self.start_epoch)
        sparsity = self.final_sparsity + (self.initial_sparsity - self.final_sparsity) * \
                   (1 - progress) ** 3
        return sparsity

    def prune_step(self, epoch):
        """Apply pruning at current epoch"""
        if epoch % self.frequency != 0:
            return

        sparsity = self.compute_sparsity(epoch)
        magnitude_prune(self.model, sparsity)

        print(f"Epoch {epoch}: Applied {sparsity:.2%} sparsity")

# Training loop with gradual pruning
pruner = GradualPruner(model, final_sparsity=0.9, end_epoch=100)

for epoch in range(num_epochs):
    # Train
    train_one_epoch(model, train_loader, optimizer)

    # Prune
    pruner.prune_step(epoch)

    # Fine-tune
    evaluate(model, val_loader)
```

### 2.3 Iterative Magnitude Pruning (IMP)

Lottery Ticket Hypothesis: Prune, retrain, repeat.

```python
def iterative_magnitude_pruning(model, train_fn, prune_rate=0.2, iterations=5):
    """
    Iterative pruning with rewinding to initial weights

    Lottery Ticket Hypothesis: winning tickets exist that train well when sparse
    """
    # Save initial weights
    initial_state = {k: v.clone() for k, v in model.state_dict().items()}

    current_sparsity = 0

    for iteration in range(iterations):
        print(f"\\n=== Pruning Iteration {iteration+1}/{iterations} ===")

        # Train model
        train_fn(model)

        # Prune
        target_sparsity = 1 - (1 - current_sparsity) * (1 - prune_rate)
        magnitude_prune(model, target_sparsity)
        current_sparsity = target_sparsity

        print(f"Current sparsity: {current_sparsity:.2%}")

        # Rewind to initial weights (but keep mask)
        for name, param in model.named_parameters():
            if 'mask' not in name:
                param.data = initial_state[name].clone()

        # Evaluate
        accuracy = evaluate(model, val_loader)
        print(f"Accuracy: {accuracy:.2%}")

    return model

# Usage
model = YourModel()
pruned_model = iterative_magnitude_pruning(
    model,
    train_fn=lambda m: train(m, train_loader, epochs=10),
    prune_rate=0.2,  # Prune 20% each iteration
    iterations=5      # 67% final sparsity: (1-0.2)^5
)
```

<a name="structured-vs-unstructured"></a>
## 3. Structured vs Unstructured Pruning

### 3.1 Unstructured Pruning

Remove individual weights, creating irregular sparsity patterns.

**Advantages**:
- Maximum flexibility
- Can achieve highest sparsity (90%+)
- Simple implementation

**Disadvantages**:
- Requires specialized sparse kernels for speedup
- Memory savings only with compressed storage
- Limited hardware support

```python
# Unstructured pruning example
# Before: Dense weight matrix
weight = torch.randn(512, 512)  # 262,144 parameters

# After 75% unstructured pruning
mask = (torch.rand_like(weight) > 0.75).float()
weight_sparse = weight * mask  # 65,536 non-zero parameters

# Still stored as dense tensor → no memory savings unless compressed
# Needs sparse matrix multiplication for speedup
```

### 3.2 Structured Pruning

Remove entire structural units (channels, filters, heads).

**Advantages**:
- Immediate speedup without sparse kernels
- True memory reduction
- Works on any hardware

**Disadvantages**:
- Less flexible
- Lower maximum sparsity (typ. 50-70%)
- More complex to implement

```python
def prune_channels(model, layer_name, channels_to_prune):
    """
    Structured pruning: Remove entire channels
    """
    layer = dict(model.named_modules())[layer_name]

    # Get weight shape: [out_channels, in_channels, kernel_h, kernel_w]
    weight = layer.weight.data
    out_ch, in_ch, kh, kw = weight.shape

    # Rank channels by importance (L1 norm)
    channel_importance = weight.abs().sum(dim=[1, 2, 3])

    # Select channels to keep
    keep_channels = torch.argsort(channel_importance, descending=True)
    keep_channels = keep_channels[:out_ch - channels_to_prune]

    # Create new layer with fewer channels
    new_layer = nn.Conv2d(
        in_channels=in_ch,
        out_channels=len(keep_channels),
        kernel_size=(kh, kw),
        stride=layer.stride,
        padding=layer.padding,
        bias=layer.bias is not None
    )

    # Copy weights for kept channels
    new_layer.weight.data = weight[keep_channels]
    if layer.bias is not None:
        new_layer.bias.data = layer.bias.data[keep_channels]

    # Replace layer in model
    set_module_by_name(model, layer_name, new_layer)

    # Also need to adjust next layer's input channels!
    adjust_next_layer(model, layer_name, keep_channels)

    return model
```

### 3.3 N:M Sparsity

Structured sparsity pattern: N non-zero values in every M consecutive values.

**2:4 Sparsity** (supported by NVIDIA Ampere+):
- Exactly 2 non-zero in every 4 consecutive values
- 50% sparsity
- 2x speedup with Tensor Cores
- Minimal accuracy loss

```python
import torch.nn.utils.prune as prune

def apply_2_4_sparsity(model):
    """
    Apply 2:4 structured sparsity (NVIDIA Ampere optimization)
    """
    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            weight = module.weight

            # Reshape to groups of 4
            shape = weight.shape
            weight_flat = weight.flatten()

            # Ensure divisible by 4
            if len(weight_flat) % 4 != 0:
                pad = 4 - (len(weight_flat) % 4)
                weight_flat = torch.nn.functional.pad(weight_flat, (0, pad))

            # Reshape to [n, 4]
            weight_groups = weight_flat.reshape(-1, 4)

            # Keep top-2 magnitude values per group
            _, indices = torch.topk(torch.abs(weight_groups), k=2, dim=1)

            # Create mask
            mask = torch.zeros_like(weight_groups)
            mask.scatter_(1, indices, 1.0)

            # Apply mask
            weight_groups.mul_(mask)

            # Reshape back
            weight_flat = weight_groups.flatten()[:shape.numel()]
            module.weight.data = weight_flat.reshape(shape)

    return model

# Automatically get 2x speedup on A100/H100 GPUs!
```

<a name="pruning-algorithms"></a>
## 4. Pruning Algorithms

### 4.1 First-Order Pruning (Magnitude-based)

Already covered - simplest and most common.

### 4.2 Second-Order Pruning (Hessian-based)

Use second-order information for better pruning decisions.

**Optimal Brain Damage (OBD)**:
```python
def optimal_brain_damage_pruning(model, data_loader, sparsity=0.5):
    """
    OBD: Prune weights with smallest effect on loss (using Hessian diagonal)
    """
    # Compute Hessian diagonal approximation
    model.zero_grad()

    # Compute gradients squared (proxy for Hessian diagonal)
    for data, target in data_loader:
        output = model(data)
        loss = criterion(output, target)
        loss.backward()

    # For each layer, compute saliency: s_i = (w_i^2 * H_ii) / 2
    saliencies = {}
    for name, param in model.named_parameters():
        if param.grad is not None:
            # Approximation: H_ii ≈ grad^2
            saliency = (param.data ** 2) * (param.grad.data ** 2) / 2
            saliencies[name] = saliency

    # Prune weights with lowest saliency
    all_saliencies = torch.cat([s.flatten() for s in saliencies.values()])
    threshold = torch.quantile(all_saliencies, sparsity)

    for name, param in model.named_parameters():
        if name in saliencies:
            mask = saliencies[name] > threshold
            param.data.mul_(mask)

    return model
```

### 4.3 Movement Pruning

Prune weights that don't move significantly during training.

```python
class MovementPruning:
    """
    Prune weights that don't change much during training
    """
    def __init__(self, model, final_sparsity=0.9):
        self.model = model
        self.final_sparsity = final_sparsity
        self.initial_weights = {}

        # Store initial weights
        for name, param in model.named_parameters():
            self.initial_weights[name] = param.data.clone()

    def compute_movement_scores(self):
        """
        Score = change in weight magnitude
        """
        scores = {}
        for name, param in self.model.named_parameters():
            if name in self.initial_weights:
                # Movement score: |w_t| - |w_0|
                initial_mag = torch.abs(self.initial_weights[name])
                current_mag = torch.abs(param.data)
                movement = current_mag - initial_mag
                scores[name] = movement
        return scores

    def prune(self):
        """Apply pruning based on movement scores"""
        scores = self.compute_movement_scores()

        all_scores = torch.cat([s.flatten() for s in scores.values()])
        threshold = torch.quantile(all_scores, self.final_sparsity)

        for name, param in self.model.named_parameters():
            if name in scores:
                mask = scores[name] > threshold
                param.data.mul_(mask)
```

<a name="distillation"></a>
## 5. Knowledge Distillation

Train small "student" model to mimic large "teacher" model.

### 5.1 Classic Knowledge Distillation

```python
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, labels,
                     temperature=3.0, alpha=0.5):
    """
    Knowledge distillation loss

    Args:
        student_logits: Student model outputs (raw logits)
        teacher_logits: Teacher model outputs (raw logits)
        labels: Ground truth labels
        temperature: Softening temperature (higher = softer)
        alpha: Weight between distillation and task loss
    """
    # Soft targets from teacher
    soft_teacher = F.softmax(teacher_logits / temperature, dim=1)
    soft_student = F.log_softmax(student_logits / temperature, dim=1)

    # Distillation loss (KL divergence)
    distill_loss = F.kl_div(
        soft_student,
        soft_teacher,
        reduction='batchmean'
    ) * (temperature ** 2)

    # Task loss (standard cross-entropy)
    task_loss = F.cross_entropy(student_logits, labels)

    # Combined loss
    loss = alpha * distill_loss + (1 - alpha) * task_loss

    return loss

# Training loop
teacher = TeacherModel()
teacher.load_state_dict(torch.load('teacher.pth'))
teacher.eval()

student = StudentModel()  # Much smaller model
optimizer = torch.optim.Adam(student.parameters())

for epoch in range(num_epochs):
    for data, labels in train_loader:
        # Get teacher predictions (no gradients needed)
        with torch.no_grad():
            teacher_logits = teacher(data)

        # Get student predictions
        student_logits = student(data)

        # Compute distillation loss
        loss = distillation_loss(student_logits, teacher_logits, labels)

        # Backprop and update
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

### 5.2 Why Distillation Works

**Dark Knowledge**: Teacher's soft predictions contain more information than hard labels.

```python
# Example: MNIST digit classification
# Hard label: [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]  # digit "3"

# Teacher soft predictions:
# [0.01, 0.01, 0.05, 0.80, 0.05, 0.03, 0.01, 0.01, 0.02, 0.01]
#  0     1     2     3     4     5     6     7     8     9
#
# "Dark knowledge":
# - "3" is most likely (0.80)
# - But "2", "4", "5" also somewhat similar (curvy shapes)
# - "1", "6", "7" very unlikely (different structure)
#
# Student learns these similarities, generalizes better
```

### 5.3 Feature-Based Distillation

Transfer intermediate representations, not just final outputs.

```python
class FeatureDistillation(nn.Module):
    """
    Distill intermediate layer features
    """
    def __init__(self, teacher, student, feature_layers):
        super().__init__()
        self.teacher = teacher
        self.student = student
        self.feature_layers = feature_layers

        # Projection layers to match dimensions
        self.projections = nn.ModuleDict()
        for layer_name in feature_layers:
            teacher_dim = get_layer_output_dim(teacher, layer_name)
            student_dim = get_layer_output_dim(student, layer_name)

            self.projections[layer_name] = nn.Linear(student_dim, teacher_dim)

    def forward(self, x, labels):
        # Extract teacher features
        teacher_features = {}
        def teacher_hook(name):
            def hook(module, input, output):
                teacher_features[name] = output.detach()
            return hook

        hooks = []
        for name in self.feature_layers:
            layer = get_layer(self.teacher, name)
            hooks.append(layer.register_forward_hook(teacher_hook(name)))

        with torch.no_grad():
            teacher_output = self.teacher(x)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        # Extract student features
        student_features = {}
        def student_hook(name):
            def hook(module, input, output):
                student_features[name] = output
            return hook

        hooks = []
        for name in self.feature_layers:
            layer = get_layer(self.student, name)
            hooks.append(layer.register_forward_hook(student_hook(name)))

        student_output = self.student(x)

        for hook in hooks:
            hook.remove()

        # Compute feature distillation loss
        feature_loss = 0
        for name in self.feature_layers:
            student_feat = self.projections[name](student_features[name])
            teacher_feat = teacher_features[name]

            # MSE loss between features
            feature_loss += F.mse_loss(student_feat, teacher_feat)

        # Task loss
        task_loss = F.cross_entropy(student_output, labels)

        # Combined loss
        total_loss = task_loss + 0.1 * feature_loss

        return total_loss, student_output
```

<a name="advanced-distillation"></a>
## 6. Advanced Distillation Techniques

### 6.1 Self-Distillation

Use model's own predictions from earlier training stages.

```python
def self_distillation(model, train_loader, epochs=100, checkpoint_epochs=10):
    """
    Self-distillation: Use earlier version of same model as teacher
    """
    teacher_checkpoints = []

    for epoch in range(epochs):
        # Save checkpoint periodically
        if epoch % checkpoint_epochs == 0 and epoch > 0:
            teacher_checkpoints.append(copy.deepcopy(model))

        for data, labels in train_loader:
            # Standard training
            output = model(data)
            task_loss = F.cross_entropy(output, labels)

            # Distillation from checkpoints
            distill_loss = 0
            if teacher_checkpoints:
                with torch.no_grad():
                    # Average predictions from all checkpoints
                    ensemble_logits = torch.stack([
                        ckpt(data) for ckpt in teacher_checkpoints
                    ]).mean(dim=0)

                distill_loss = F.kl_div(
                    F.log_softmax(output / 3, dim=1),
                    F.softmax(ensemble_logits / 3, dim=1),
                    reduction='batchmean'
                ) * 9

            loss = task_loss + 0.1 * distill_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
```

### 6.2 Online Distillation

Teacher and student train simultaneously.

```python
class OnlineDistillation:
    """
    Train teacher and student together
    Teacher learns better, student learns from teacher
    """
    def __init__(self, teacher, student):
        self.teacher = teacher
        self.student = student
        self.teacher_optimizer = torch.optim.Adam(teacher.parameters(), lr=0.001)
        self.student_optimizer = torch.optim.Adam(student.parameters(), lr=0.001)

    def train_step(self, data, labels):
        # Train teacher normally
        teacher_output = self.teacher(data)
        teacher_loss = F.cross_entropy(teacher_output, labels)

        self.teacher_optimizer.zero_grad()
        teacher_loss.backward()
        self.teacher_optimizer.step()

        # Train student with distillation
        student_output = self.student(data)

        # Detach teacher output (don't backprop through teacher)
        distill_loss = F.kl_div(
            F.log_softmax(student_output / 3, dim=1),
            F.softmax(teacher_output.detach() / 3, dim=1),
            reduction='batchmean'
        ) * 9

        task_loss = F.cross_entropy(student_output, labels)
        student_loss = 0.5 * task_loss + 0.5 * distill_loss

        self.student_optimizer.zero_grad()
        student_loss.backward()
        self.student_optimizer.step()

        return teacher_loss.item(), student_loss.item()
```

### 6.3 Distillation for LLMs

Specialized techniques for large language models.

```python
def llm_distillation(teacher_model, student_model, train_data,
                     temperature=2.0, top_p=0.95):
    """
    Distillation for autoregressive LLMs

    Teacher: Large model (70B parameters)
    Student: Small model (7B parameters)
    """
    for batch in train_data:
        input_ids = batch['input_ids']

        # Get teacher predictions (distribution over vocabulary)
        with torch.no_grad():
            teacher_logits = teacher_model(input_ids).logits

        # Get student predictions
        student_logits = student_model(input_ids).logits

        # Sequence-level distillation
        # For each position, distill next-token distribution

        # Shift logits and labels for next-token prediction
        shift_logits_teacher = teacher_logits[..., :-1, :].contiguous()
        shift_logits_student = student_logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()

        # Distillation loss
        loss_distill = F.kl_div(
            F.log_softmax(shift_logits_student / temperature, dim=-1),
            F.softmax(shift_logits_teacher / temperature, dim=-1),
            reduction='batchmean'
        ) * (temperature ** 2)

        # Task loss (standard language modeling)
        loss_lm = F.cross_entropy(
            shift_logits_student.view(-1, shift_logits_student.size(-1)),
            shift_labels.view(-1)
        )

        loss = 0.5 * loss_distill + 0.5 * loss_lm

        # Optimize student
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

<a name="low-rank"></a>
## 7. Low-Rank Factorization

Decompose weight matrices to reduce parameters.

### 7.1 SVD Factorization

```python
def low_rank_factorize_layer(layer, rank_ratio=0.5):
    """
    Factorize a linear/conv layer using SVD

    W ∈ R^(m×n) → U ∈ R^(m×r), V ∈ R^(r×n) where r << min(m,n)
    """
    weight = layer.weight.data

    # Reshape convolution weights to 2D if needed
    if len(weight.shape) == 4:
        out_ch, in_ch, kh, kw = weight.shape
        weight_2d = weight.reshape(out_ch, -1)
    else:
        weight_2d = weight
        out_ch, in_ch = weight.shape

    # SVD
    U, S, V = torch.svd(weight_2d)

    # Keep top-k singular values
    rank = int(min(weight_2d.shape) * rank_ratio)

    U_low = U[:, :rank]
    S_low = S[:rank]
    V_low = V[:, :rank]

    # Reconstruct as two matrices: U_low @ (S_low * V_low^T)
    W1 = U_low @ torch.diag(torch.sqrt(S_low))
    W2 = torch.diag(torch.sqrt(S_low)) @ V_low.t()

    # Create two sequential layers
    if isinstance(layer, nn.Linear):
        layer1 = nn.Linear(in_ch, rank, bias=False)
        layer2 = nn.Linear(rank, out_ch, bias=(layer.bias is not None))

        layer1.weight.data = W2
        layer2.weight.data = W1
        if layer.bias is not None:
            layer2.bias.data = layer.bias.data

    # Parameters: m*n → m*r + r*n (savings when r << min(m,n))
    return nn.Sequential(layer1, layer2)
```

<a name="peft"></a>
## 8. Parameter-Efficient Fine-Tuning (PEFT)

### 8.1 LoRA (Low-Rank Adaptation)

Add low-rank trainable matrices to frozen pre-trained weights.

```python
class LoRALinear(nn.Module):
    """
    LoRA: Add low-rank adaptation matrices

    W' = W + ΔW where ΔW = A @ B
    A ∈ R^(d×r), B ∈ R^(r×k), r << min(d,k)
    """
    def __init__(self, in_features, out_features, rank=8, alpha=16):
        super().__init__()

        # Original weights (frozen)
        self.linear = nn.Linear(in_features, out_features)
        self.linear.weight.requires_grad = False
        if self.linear.bias is not None:
            self.linear.bias.requires_grad = False

        # LoRA parameters (trainable)
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))

        self.rank = rank
        self.scaling = alpha / rank

    def forward(self, x):
        # Original output
        output = self.linear(x)

        # Add LoRA adaptation
        lora_output = (x @ self.lora_A @ self.lora_B) * self.scaling

        return output + lora_output

    def merge_weights(self):
        """Merge LoRA weights into original weights for deployment"""
        self.linear.weight.data += (self.lora_A @ self.lora_B).t() * self.scaling

# Apply LoRA to model
def apply_lora(model, rank=8, target_modules=['q_proj', 'v_proj']):
    """
    Replace linear layers with LoRA versions
    """
    for name, module in model.named_modules():
        if any(target in name for target in target_modules):
            if isinstance(module, nn.Linear):
                lora_layer = LoRALinear(
                    module.in_features,
                    module.out_features,
                    rank=rank
                )
                lora_layer.linear = module
                set_module_by_name(model, name, lora_layer)

    return model

# Training: Only LoRA parameters updated
model = apply_lora(pretrained_model, rank=8)
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print(f"Trainable: {trainable_params/1e6:.1f}M / {total_params/1e6:.1f}M")
# Typical: 0.5M trainable / 70B total = 0.0007% parameters
```

### 8.2 QLoRA (Quantized LoRA)

Combine quantization with LoRA for extreme efficiency.

```python
from transformers import BitsAndBytesConfig

# Load model in 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

# Apply LoRA on top
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Now can fine-tune 70B model on single GPU!
# Base model: 4-bit (70B → 35GB)
# LoRA params: FP16 (1M params = 2MB)
# Total: ~35GB vs 140GB for full fine-tuning
```

<a name="combining"></a>
## 9. Combining Compression Techniques

Multiple techniques can be combined for maximum compression.

```python
def compress_model_pipeline(model, train_loader, val_loader):
    """
    Multi-stage compression pipeline
    """
    print("Stage 1: Knowledge Distillation")
    # Train small student from large teacher
    student = SmallModel()
    distill_train(teacher=model, student=student, data=train_loader)

    print("Stage 2: Quantization-Aware Training")
    # QAT on student model
    student.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
    student = torch.quantization.prepare_qat(student)
    train(student, train_loader, epochs=5)
    student = torch.quantization.convert(student)

    print("Stage 3: Pruning")
    # Structured pruning
    student = structured_prune(student, sparsity=0.5)

    # Fine-tune
    train(student, train_loader, epochs=5)

    print("Stage 4: Low-Rank Factorization")
    # Factorize remaining large layers
    for name, module in student.named_modules():
        if isinstance(module, nn.Linear) and module.in_features > 1024:
            factorized = low_rank_factorize_layer(module, rank_ratio=0.5)
            set_module_by_name(student, name, factorized)

    # Final fine-tune
    train(student, train_loader, epochs=2)

    # Evaluate
    accuracy = evaluate(student, val_loader)

    # Measure compression
    original_size = get_model_size(model)
    compressed_size = get_model_size(student)
    compression_ratio = original_size / compressed_size

    print(f"\\nCompression Results:")
    print(f"Original: {original_size/1e6:.1f}MB")
    print(f"Compressed: {compressed_size/1e6:.1f}MB")
    print(f"Ratio: {compression_ratio:.1f}x")
    print(f"Accuracy: {accuracy:.2%}")

    return student
```

<a name="production"></a>
## 10. Production Considerations

### Deployment Checklist

```python
def validate_compressed_model(original, compressed, test_data):
    """
    Comprehensive validation before deploying compressed model
    """
    results = {}

    # 1. Accuracy
    results['accuracy_original'] = evaluate_accuracy(original, test_data)
    results['accuracy_compressed'] = evaluate_accuracy(compressed, test_data)
    results['accuracy_drop'] = results['accuracy_original'] - results['accuracy_compressed']

    # 2. Latency
    results['latency_original'] = benchmark_latency(original, test_data)
    results['latency_compressed'] = benchmark_latency(compressed, test_data)
    results['speedup'] = results['latency_original'] / results['latency_compressed']

    # 3. Memory
    results['memory_original'] = get_model_size(original)
    results['memory_compressed'] = get_model_size(compressed)
    results['compression_ratio'] = results['memory_original'] / results['memory_compressed']

    # 4. Throughput
    results['throughput_original'] = benchmark_throughput(original)
    results['throughput_compressed'] = benchmark_throughput(compressed)

    # 5. Per-class accuracy (check for biases)
    results['per_class_acc_original'] = per_class_accuracy(original, test_data)
    results['per_class_acc_compressed'] = per_class_accuracy(compressed, test_data)

    return results
```

## Summary

Model compression via pruning and distillation:

- **Pruning**: Remove unnecessary parameters (50-90% sparsity typical)
- **Distillation**: Train small models from large teachers (2-10x smaller)
- **Low-Rank**: Factorize weight matrices (2-4x compression)
- **PEFT**: LoRA/QLoRA for efficient adaptation (99%+ fewer parameters)
- **Combinations**: Multiple techniques compound benefits

These techniques complement quantization for maximum efficiency!

## Next Steps

1. Complete Lab 03: Implement pruning and distillation
2. Read Lecture 06: LLM-Specific Optimizations
3. Experiment with compression pipelines

---

**Lecture Duration**: 6 hours
**Difficulty**: Advanced
