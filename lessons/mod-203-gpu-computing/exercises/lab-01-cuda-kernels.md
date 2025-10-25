# Lab 01: Writing Custom CUDA Kernels for ML Operations

## Lab Overview

**Duration**: 3-4 hours
**Difficulty**: Intermediate
**Prerequisites**: Lecture 01 (CUDA Fundamentals), basic C++ knowledge

In this lab, you will write custom CUDA kernels for common ML operations, gaining hands-on experience with GPU programming.

## Learning Objectives

By completing this lab, you will:
1. Write CUDA kernels from scratch for ML operations
2. Understand memory access patterns and optimization
3. Use shared memory for performance optimization
4. Benchmark and compare kernel performance
5. Integrate custom CUDA kernels with PyTorch

## Lab Environment Setup

### Required Software
- CUDA Toolkit 11.8+ or 12.0+
- GCC/G++ compiler
- PyTorch 2.0+ with CUDA support
- Python 3.8+
- nvidia-smi

### Verify Installation

```bash
# Check CUDA version
nvcc --version

# Check GPU availability
nvidia-smi

# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

## Part 1: Vector Operations

### Exercise 1.1: Element-wise Operations

Write CUDA kernels for basic element-wise operations.

**Task**: Implement ReLU activation function

```cpp
// relu_kernel.cu
#include <cuda_runtime.h>
#include <stdio.h>

// TODO: Implement ReLU kernel
// ReLU(x) = max(0, x)
__global__ void reluKernel(const float* input, float* output, int N) {
    // TODO: Calculate global thread index
    int idx = 0; // IMPLEMENT THIS

    // TODO: Boundary check
    if (idx < N) {
        // TODO: Implement ReLU operation
        output[idx] = 0.0f; // IMPLEMENT THIS
    }
}

// Host wrapper function
void reluCUDA(const float* d_input, float* d_output, int N) {
    // TODO: Calculate grid and block dimensions
    int threadsPerBlock = 256;
    int blocksPerGrid = 0; // IMPLEMENT THIS

    // TODO: Launch kernel
    reluKernel<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, N);

    // TODO: Check for kernel launch errors
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("ReLU kernel launch error: %s\n", cudaGetErrorString(err));
    }
}

// Test function
int main() {
    int N = 1000000;
    size_t size = N * sizeof(float);

    // TODO: Allocate host memory
    float *h_input, *h_output;
    // IMPLEMENT ALLOCATION

    // TODO: Initialize input with random values (including negatives)
    for (int i = 0; i < N; i++) {
        h_input[i] = (float)rand() / RAND_MAX * 2.0f - 1.0f; // Range: -1 to 1
    }

    // TODO: Allocate device memory
    float *d_input, *d_output;
    // IMPLEMENT ALLOCATION

    // TODO: Copy input to device
    // IMPLEMENT COPY

    // TODO: Launch kernel
    reluCUDA(d_input, d_output, N);

    // TODO: Copy result back to host
    // IMPLEMENT COPY

    // TODO: Verify correctness (check first 10 elements)
    printf("Verification (first 10 elements):\n");
    for (int i = 0; i < 10; i++) {
        float expected = (h_input[i] > 0) ? h_input[i] : 0.0f;
        printf("Input: %.4f, Output: %.4f, Expected: %.4f %s\n",
               h_input[i], h_output[i], expected,
               (fabs(h_output[i] - expected) < 1e-5) ? "✓" : "✗");
    }

    // TODO: Free memory
    // IMPLEMENT CLEANUP

    return 0;
}
```

**Compile and Run:**
```bash
nvcc -o relu relu_kernel.cu
./relu
```

**Expected Output:**
```
Verification (first 10 elements):
Input: -0.3412, Output: 0.0000, Expected: 0.0000 ✓
Input: 0.7651, Output: 0.7651, Expected: 0.7651 ✓
...
```

### Exercise 1.2: Sigmoid Activation

**Task**: Implement sigmoid activation with gradient computation

```cpp
// sigmoid_kernel.cu

// TODO: Implement sigmoid kernel
// sigmoid(x) = 1 / (1 + exp(-x))
__global__ void sigmoidKernel(const float* input, float* output, int N) {
    // TODO: IMPLEMENT THIS
}

// TODO: Implement sigmoid gradient kernel
// gradient(x) = sigmoid(x) * (1 - sigmoid(x))
__global__ void sigmoidGradientKernel(const float* input, const float* grad_output,
                                       float* grad_input, int N) {
    // TODO: IMPLEMENT THIS
}

// TODO: Implement test main function
int main() {
    // Test both forward and backward pass
    // TODO: IMPLEMENT TESTS
    return 0;
}
```

## Part 2: Matrix Operations

### Exercise 2.1: Matrix Transpose

**Task**: Implement efficient matrix transpose using shared memory

```cpp
// transpose_kernel.cu

#define TILE_SIZE 32

// Naive transpose (global memory only)
__global__ void transposeNaive(const float* input, float* output, int M, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < N) {
        output[col * M + row] = input[row * N + col];
    }
}

// TODO: Implement optimized transpose with shared memory
__global__ void transposeShared(const float* input, float* output, int M, int N) {
    // TODO: Declare shared memory tile
    __shared__ float tile[TILE_SIZE][TILE_SIZE + 1]; // +1 to avoid bank conflicts

    // TODO: Calculate global row and col
    int row = 0; // IMPLEMENT
    int col = 0; // IMPLEMENT

    // TODO: Load tile from global memory to shared memory
    // IMPLEMENT

    // TODO: Synchronize threads
    __syncthreads();

    // TODO: Calculate transposed position
    int transposed_row = 0; // IMPLEMENT
    int transposed_col = 0; // IMPLEMENT

    // TODO: Write transposed tile from shared memory to global memory
    // IMPLEMENT
}

// Benchmark function
void benchmarkTranspose(int M, int N) {
    // TODO: Implement benchmarking
    // Compare naive vs. shared memory version
    // Measure bandwidth and speedup
}

int main() {
    // TODO: Test transpose with different sizes
    // Compare performance of naive vs. optimized
    return 0;
}
```

### Exercise 2.2: Matrix Multiplication

**Task**: Implement tiled matrix multiplication

```cpp
// matmul_kernel.cu

#define TILE_WIDTH 16

// TODO: Implement naive matrix multiplication
// C = A * B, where A is M×K, B is K×N, C is M×N
__global__ void matmulNaive(const float* A, const float* B, float* C,
                             int M, int K, int N) {
    // TODO: IMPLEMENT THIS
}

// TODO: Implement tiled matrix multiplication with shared memory
__global__ void matmulTiled(const float* A, const float* B, float* C,
                             int M, int K, int N) {
    // TODO: Declare shared memory for tiles
    __shared__ float tileA[TILE_WIDTH][TILE_WIDTH];
    __shared__ float tileB[TILE_WIDTH][TILE_WIDTH];

    // TODO: Calculate row and col
    int row = 0; // IMPLEMENT
    int col = 0; // IMPLEMENT

    float sum = 0.0f;

    // TODO: Loop over tiles
    for (int t = 0; t < (K + TILE_WIDTH - 1) / TILE_WIDTH; t++) {
        // TODO: Load tiles into shared memory
        // IMPLEMENT

        // TODO: Synchronize
        __syncthreads();

        // TODO: Compute partial dot product
        // IMPLEMENT

        // TODO: Synchronize before loading next tile
        __syncthreads();
    }

    // TODO: Write result
    if (row < M && col < N) {
        C[row * N + col] = sum;
    }
}

// Benchmark function
void benchmarkMatmul(int M, int K, int N) {
    // TODO: Compare naive vs. tiled vs. cuBLAS
}

int main() {
    // TODO: Test and benchmark matrix multiplication
    return 0;
}
```

## Part 3: Reduction Operations

### Exercise 3.1: Vector Sum

**Task**: Implement parallel reduction for vector sum

```cpp
// reduction_kernel.cu

// TODO: Implement reduction kernel (sum)
__global__ void reduceSum(const float* input, float* output, int N) {
    // TODO: Declare shared memory
    extern __shared__ float sdata[];

    // TODO: Load data into shared memory
    int tid = threadIdx.x;
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = (idx < N) ? input[idx] : 0.0f;
    __syncthreads();

    // TODO: Implement reduction in shared memory
    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            // TODO: IMPLEMENT REDUCTION STEP
        }
        __syncthreads();
    }

    // TODO: Write result of this block
    if (tid == 0) {
        output[blockIdx.x] = sdata[0];
    }
}

// Host function
float vectorSum(const float* d_input, int N) {
    // TODO: Implement multi-stage reduction
    // Stage 1: Reduce to one value per block
    // Stage 2: Reduce block results to final sum
    return 0.0f; // IMPLEMENT
}

int main() {
    // TODO: Test reduction
    // Compare with CPU sum for verification
    return 0;
}
```

## Part 4: Advanced Operations

### Exercise 4.1: Softmax

**Task**: Implement numerically stable softmax

```cpp
// softmax_kernel.cu

// TODO: Implement max reduction (for numerical stability)
__global__ void maxReduce(const float* input, float* output, int batch_size, int dim) {
    // TODO: Find max value per batch
    // Use shared memory reduction
}

// TODO: Implement exp and sum
__global__ void expAndSum(const float* input, const float* max_vals,
                          float* exp_vals, float* sum_vals,
                          int batch_size, int dim) {
    // TODO: Compute exp(x - max) and sum
}

// TODO: Implement normalization
__global__ void normalize(const float* exp_vals, const float* sum_vals,
                          float* output, int batch_size, int dim) {
    // TODO: Divide by sum to get softmax
}

// Host wrapper
void softmaxCUDA(const float* d_input, float* d_output, int batch_size, int dim) {
    // TODO: Orchestrate three-stage softmax
    // 1. Find max
    // 2. Compute exp and sum
    // 3. Normalize
}

int main() {
    // TODO: Test softmax
    // Verify output sums to 1.0 for each batch
    return 0;
}
```

### Exercise 4.2: Layer Normalization

**Task**: Implement layer normalization

```cpp
// layernorm_kernel.cu

// TODO: Implement mean and variance computation
__global__ void computeMeanVar(const float* input, float* mean, float* var,
                               int batch_size, int dim) {
    // TODO: Compute mean and variance for each batch
}

// TODO: Implement normalization
__global__ void layerNorm(const float* input, const float* mean, const float* var,
                          const float* gamma, const float* beta,
                          float* output, int batch_size, int dim, float eps) {
    // TODO: output = gamma * (input - mean) / sqrt(var + eps) + beta
}

int main() {
    // TODO: Test layer normalization
    return 0;
}
```

## Part 5: PyTorch Integration

### Exercise 5.1: Custom CUDA Extension

**Task**: Integrate custom CUDA kernels with PyTorch

**File Structure:**
```
custom_ops/
├── setup.py
├── relu_cuda.cu
└── relu_cuda.cpp
```

**relu_cuda.cu:**
```cpp
#include <torch/extension.h>
#include <cuda_runtime.h>

__global__ void relu_kernel(const float* input, float* output, int size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size) {
        output[idx] = fmaxf(0.0f, input[idx]);
    }
}

__global__ void relu_backward_kernel(const float* grad_output, const float* input,
                                      float* grad_input, int size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size) {
        grad_input[idx] = (input[idx] > 0) ? grad_output[idx] : 0.0f;
    }
}

torch::Tensor relu_cuda_forward(torch::Tensor input) {
    auto output = torch::zeros_like(input);
    int size = input.numel();
    int threads = 256;
    int blocks = (size + threads - 1) / threads;

    relu_kernel<<<blocks, threads>>>(
        input.data_ptr<float>(),
        output.data_ptr<float>(),
        size
    );

    return output;
}

torch::Tensor relu_cuda_backward(torch::Tensor grad_output, torch::Tensor input) {
    // TODO: Implement backward pass
    return torch::zeros_like(input); // IMPLEMENT
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("forward", &relu_cuda_forward, "ReLU forward (CUDA)");
    m.def("backward", &relu_cuda_backward, "ReLU backward (CUDA)");
}
```

**setup.py:**
```python
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name='relu_cuda',
    ext_modules=[
        CUDAExtension('relu_cuda', [
            'relu_cuda.cu',
        ])
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)
```

**Test script:**
```python
# test_custom_relu.py
import torch
import relu_cuda
import time

def test_correctness():
    """Test that custom CUDA ReLU matches PyTorch"""
    x = torch.randn(1000000).cuda()

    # PyTorch ReLU
    torch_out = torch.relu(x)

    # Custom CUDA ReLU
    custom_out = relu_cuda.forward(x)

    # Compare
    assert torch.allclose(torch_out, custom_out, atol=1e-5)
    print("✓ Correctness test passed")

def benchmark():
    """Benchmark custom vs PyTorch ReLU"""
    sizes = [10000, 100000, 1000000, 10000000]

    for size in sizes:
        x = torch.randn(size).cuda()

        # Warm up
        for _ in range(10):
            torch.relu(x)
            relu_cuda.forward(x)

        # Benchmark PyTorch
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(100):
            torch.relu(x)
        torch.cuda.synchronize()
        torch_time = (time.time() - start) / 100

        # Benchmark custom
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(100):
            relu_cuda.forward(x)
        torch.cuda.synchronize()
        custom_time = (time.time() - start) / 100

        print(f"Size: {size:>10}, PyTorch: {torch_time*1000:.3f}ms, "
              f"Custom: {custom_time*1000:.3f}ms, "
              f"Speedup: {torch_time/custom_time:.2f}x")

if __name__ == "__main__":
    test_correctness()
    benchmark()
```

**Build and run:**
```bash
# Build extension
python setup.py install

# Run tests
python test_custom_relu.py
```

## Part 6: Performance Analysis

### Exercise 6.1: Profile Your Kernels

Use Nsight Compute to profile your kernels:

```bash
# Profile ReLU kernel
ncu --set full -o relu_profile python test_custom_relu.py

# Open in GUI
ncu-ui relu_profile.ncu-rep
```

**TODO: Answer these questions:**
1. What is the achieved occupancy?
2. Is the kernel memory-bound or compute-bound?
3. What is the DRAM bandwidth utilization?
4. Are there any optimization opportunities?

## Deliverables

Submit the following:

1. **Source Code**: All CUDA kernel implementations
2. **Test Results**: Output showing correctness verification
3. **Benchmarks**: Performance comparison with PyTorch/cuBLAS
4. **Profiling Report**: Nsight Compute analysis of 2-3 kernels
5. **Reflection**: Document answering:
   - Which kernel was hardest to optimize?
   - What did you learn about GPU memory access?
   - How do your kernels compare to library implementations?

## Bonus Challenges

If you finish early, try these advanced tasks:

1. **Implement Attention Mechanism**: Write CUDA kernel for scaled dot-product attention
2. **Mixed Precision**: Modify kernels to use FP16 with FP32 accumulation
3. **Warp-level Primitives**: Implement reduction using warp shuffles
4. **Multi-GPU**: Extend kernels to work across multiple GPUs with NCCL

## Resources

- CUDA C Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
- PyTorch CUDA Extension Tutorial: https://pytorch.org/tutorials/advanced/cpp_extension.html
- CUDA Samples: /usr/local/cuda/samples/

## Evaluation Criteria

- **Correctness** (40%): Kernels produce correct results
- **Performance** (30%): Optimized implementations with good speedup
- **Code Quality** (20%): Well-structured, commented code
- **Analysis** (10%): Insightful profiling and reflection

---

**Good luck! This lab will give you practical experience with GPU programming that's essential for optimizing ML workloads.**
