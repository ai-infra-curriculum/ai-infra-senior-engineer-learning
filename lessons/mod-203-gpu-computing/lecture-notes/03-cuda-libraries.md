# Lecture 03: CUDA Libraries for Machine Learning

## Learning Objectives

By the end of this lecture, you will be able to:

- Design production ML inference pipelines using TensorRT optimizations including layer fusion, precision calibration, and kernel auto-tuning to achieve 2-10x latency reduction
- Implement cuDNN-optimized training workflows that leverage efficient convolution algorithms, persistent RNNs, and fused operations for maximum training throughput
- Configure cuBLAS and cuSPARSE operations with optimal parameters (algorithm selection, workspace size, matrix layout) for specific model architectures
- Integrate Triton Inference Server with multiple ML frameworks (PyTorch, TensorFlow, ONNX) to build scalable multi-model serving infrastructure
- Evaluate trade-offs between different CUDA library implementations (cuDNN algorithms, TensorRT precision modes) based on accuracy, latency, and throughput requirements
- Implement mixed precision inference using TensorRT INT8 quantization with proper calibration workflows to maintain model accuracy while reducing memory and latency
- Design custom CUDA operations that integrate seamlessly with cuDNN/cuBLAS for specialized ML operations not covered by standard libraries
- Troubleshoot common CUDA library issues including version compatibility, workspace allocation failures, and algorithm selection performance problems

## Table of Contents
1. [Introduction to CUDA Libraries](#introduction-to-cuda-libraries)
2. [cuDNN - Deep Neural Network Library](#cudnn---deep-neural-network-library)
3. [cuBLAS - Linear Algebra](#cublas---linear-algebra)
4. [TensorRT - Inference Optimization](#tensorrt---inference-optimization)
5. [cuSPARSE and cuFFT](#cusparse-and-cufft)
6. [Thrust - High-Level Parallel Algorithms](#thrust---high-level-parallel-algorithms)
7. [NCCL - Multi-GPU Communication](#nccl---multi-gpu-communication)
8. [Integration with ML Frameworks](#integration-with-ml-frameworks)

## Introduction to CUDA Libraries

CUDA libraries provide highly optimized implementations of common operations used in ML workloads. Understanding these libraries helps you:

1. **Leverage existing optimizations** instead of writing custom kernels
2. **Debug performance issues** by understanding what frameworks call under the hood
3. **Choose appropriate tools** for custom ML operations
4. **Optimize inference pipelines** using TensorRT
5. **Scale training** across multiple GPUs with NCCL

### Library Ecosystem

```
Application Layer
├── PyTorch / TensorFlow / JAX
│
ML Framework Layer
├── cuDNN (Neural Network Primitives)
├── cuBLAS (Matrix Operations)
├── NCCL (Multi-GPU Communication)
│
CUDA Libraries Layer
├── cuSPARSE (Sparse Operations)
├── cuFFT (Fast Fourier Transform)
├── Thrust (STL-like algorithms)
├── cuSOLVER (Linear Solvers)
│
CUDA Runtime / Driver
│
GPU Hardware
```

### Library Versions and Compatibility

CUDA libraries are versioned with CUDA Toolkit:

```bash
# Check CUDA version
nvcc --version
cat /usr/local/cuda/version.txt

# Check library versions
ls /usr/local/cuda/lib64/libcudnn.so*
ls /usr/local/cuda/lib64/libcublas.so*

# From Python
import torch
print(torch.version.cuda)      # CUDA version
print(torch.backends.cudnn.version())  # cuDNN version
```

**Compatibility Matrix (Example):**
- CUDA 11.8: cuDNN 8.7+, cuBLAS 11.11+, TensorRT 8.5+
- CUDA 12.0: cuDNN 8.8+, cuBLAS 12.0+, TensorRT 8.6+
- CUDA 12.3: cuDNN 8.9+, cuBLAS 12.3+, TensorRT 9.0+

## cuDNN - Deep Neural Network Library

cuDNN is NVIDIA's library of primitives for deep neural networks. It's the backbone of all major ML frameworks.

### What cuDNN Provides

Core operations:
- **Convolutions**: Forward, backward data, backward filter
- **Pooling**: Max, average pooling
- **Activations**: ReLU, tanh, sigmoid, ELU, etc.
- **Normalization**: Batch norm, layer norm, instance norm
- **Softmax**: Forward and backward
- **Recurrent Networks**: LSTM, GRU cells
- **Attention**: Multi-head attention mechanisms
- **Transformers**: Fused attention operations

### cuDNN Architecture

cuDNN uses **algorithm selection** for optimal performance:

```
cuDNN API Call
    ↓
Algorithm Selection
(based on input size, hardware, etc.)
    ↓
┌─────────────────────────┐
│ GEMM-based convolution  │
│ Winograd convolution    │
│ FFT-based convolution   │
│ Direct convolution      │
│ Implicit GEMM           │
└─────────────────────────┘
    ↓
Optimized CUDA Kernel
    ↓
GPU Execution
```

### cuDNN Example: Convolution

```cpp
#include <cudnn.h>

// Initialize cuDNN
cudnnHandle_t cudnn;
cudnnCreate(&cudnn);

// Create tensor descriptors
cudnnTensorDescriptor_t input_desc, output_desc;
cudnnFilterDescriptor_t filter_desc;
cudnnConvolutionDescriptor_t conv_desc;

cudnnCreateTensorDescriptor(&input_desc);
cudnnCreateTensorDescriptor(&output_desc);
cudnnCreateFilterDescriptor(&filter_desc);
cudnnCreateConvolutionDescriptor(&conv_desc);

// Set descriptor properties
// Input: N=32, C=3, H=224, W=224
cudnnSetTensor4dDescriptor(input_desc,
    CUDNN_TENSOR_NCHW,           // Format
    CUDNN_DATA_FLOAT,            // Data type
    32, 3, 224, 224);            // N, C, H, W

// Filter: 64 output channels, 3 input channels, 3x3 kernel
cudnnSetFilter4dDescriptor(filter_desc,
    CUDNN_DATA_FLOAT,
    CUDNN_TENSOR_NCHW,
    64, 3, 3, 3);                // K, C, H, W

// Convolution: padding=1, stride=1, dilation=1
cudnnSetConvolution2dDescriptor(conv_desc,
    1, 1,                        // Padding H, W
    1, 1,                        // Stride H, W
    1, 1,                        // Dilation H, W
    CUDNN_CROSS_CORRELATION,
    CUDNN_DATA_FLOAT);

// Get output dimensions
int n, c, h, w;
cudnnGetConvolution2dForwardOutputDim(conv_desc, input_desc, filter_desc,
                                      &n, &c, &h, &w);
printf("Output dimensions: %d x %d x %d x %d\n", n, c, h, w);

// Set output descriptor
cudnnSetTensor4dDescriptor(output_desc,
    CUDNN_TENSOR_NCHW,
    CUDNN_DATA_FLOAT,
    n, c, h, w);

// Find best algorithm
int algo_count;
cudnnConvolutionFwdAlgoPerf_t algo_perf[10];
cudnnFindConvolutionForwardAlgorithm(cudnn,
    input_desc, filter_desc, conv_desc, output_desc,
    10, &algo_count, algo_perf);

// Use the fastest algorithm
cudnnConvolutionFwdAlgo_t algo = algo_perf[0].algo;
printf("Selected algorithm: %d, time: %.3f ms\n",
       algo, algo_perf[0].time);

// Get workspace size
size_t workspace_size;
cudnnGetConvolutionForwardWorkspaceSize(cudnn,
    input_desc, filter_desc, conv_desc, output_desc,
    algo, &workspace_size);

// Allocate workspace
void* workspace;
cudaMalloc(&workspace, workspace_size);

// Perform convolution
float alpha = 1.0f, beta = 0.0f;
cudnnConvolutionForward(cudnn,
    &alpha,
    input_desc, d_input,
    filter_desc, d_filter,
    conv_desc,
    algo,
    workspace, workspace_size,
    &beta,
    output_desc, d_output);

// Cleanup
cudnnDestroyTensorDescriptor(input_desc);
cudnnDestroyTensorDescriptor(output_desc);
cudnnDestroyFilterDescriptor(filter_desc);
cudnnDestroyConvolutionDescriptor(conv_desc);
cudnnDestroy(cudnn);
cudaFree(workspace);
```

### cuDNN Tensor Cores

cuDNN automatically uses Tensor Cores when available:

```cpp
// Enable Tensor Core operations (CUDA 9.0+)
cudnnSetConvolutionMathType(conv_desc, CUDNN_TENSOR_OP_MATH);

// Or use default (automatically selects best)
cudnnSetConvolutionMathType(conv_desc, CUDNN_DEFAULT_MATH);
```

**Math Types:**
- `CUDNN_DEFAULT_MATH`: Let cuDNN choose (usually uses Tensor Cores)
- `CUDNN_TENSOR_OP_MATH`: Force Tensor Cores (FP16/mixed precision)
- `CUDNN_FMA_MATH`: Force FP32 FMA units
- `CUDNN_TENSOR_OP_MATH_ALLOW_CONVERSION`: Allow FP32→FP16 conversion

### cuDNN Best Practices

1. **Reuse descriptors** across multiple operations
2. **Use algorithm search** during warmup, cache results
3. **Enable Tensor Cores** for better performance
4. **Choose appropriate data format**: NCHW vs. NHWC
5. **Tune workspace size** for memory-constrained scenarios

```python
# PyTorch: Enable cuDNN benchmarking
import torch
torch.backends.cudnn.benchmark = True  # Find best algorithm at runtime

# Disable for deterministic results
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

### cuDNN Performance Tips

**Data Layout:**
- **NCHW** (N=batch, C=channels, H=height, W=width): Traditional layout, good for conv2d
- **NHWC**: Better for Tensor Core utilization on recent GPUs
- **NCHW_VECT_C**: Vectorized channels for INT8

```cpp
// Use NHWC for Tensor Core optimization on Ampere+
cudnnSetTensor4dDescriptor(input_desc,
    CUDNN_TENSOR_NHWC,  // Better Tensor Core utilization
    CUDNN_DATA_HALF,    // FP16 for Tensor Cores
    32, 3, 224, 224);
```

## cuBLAS - Linear Algebra

cuBLAS provides GPU-accelerated BLAS (Basic Linear Algebra Subprograms) operations.

### cuBLAS Operations

**Level 1**: Vector-vector operations
- `cublasSaxpy`: y = alpha * x + y
- `cublasSdot`: dot product
- `cublasSnrm2`: L2 norm

**Level 2**: Matrix-vector operations
- `cublasSgemv`: y = alpha * A * x + beta * y

**Level 3**: Matrix-matrix operations (most important for ML)
- `cublasSgemm`: C = alpha * A * B + beta * C
- `cublasSgemmStridedBatched`: Batched matrix multiplication

### cuBLAS GEMM Example

```cpp
#include <cublas_v2.h>

// Matrix multiplication: C = A * B
// A: M x K, B: K x N, C: M x N

cublasHandle_t handle;
cublasCreate(&handle);

int M = 1024, N = 1024, K = 1024;
float alpha = 1.0f, beta = 0.0f;

// cuBLAS uses column-major (Fortran) ordering
// For row-major (C/C++): compute C^T = B^T * A^T
cublasSgemm(handle,
    CUBLAS_OP_N, CUBLAS_OP_N,  // No transpose
    N, M, K,                    // Dimensions (swapped for row-major)
    &alpha,
    d_B, N,                     // B matrix, leading dimension
    d_A, K,                     // A matrix, leading dimension
    &beta,
    d_C, N);                    // C matrix, leading dimension

cublasDestroy(handle);
```

### Batched Matrix Multiplication

Critical for transformers and attention mechanisms:

```cpp
// Batched GEMM: C[i] = A[i] * B[i] for i = 0..batchCount-1
int batchCount = 128;
int M = 64, N = 64, K = 64;

// Strided batched (arrays stored contiguously)
cublasSgemmStridedBatched(handle,
    CUBLAS_OP_N, CUBLAS_OP_N,
    N, M, K,
    &alpha,
    d_B, N, N*K,               // B matrices, stride
    d_A, K, M*K,               // A matrices, stride
    &beta,
    d_C, N, M*N,               // C matrices, stride
    batchCount);

// TODO: Implement batched matrix multiplication for attention mechanism
// Q, K, V matrices for multi-head attention
```

### cuBLAS with Tensor Cores

```cpp
// Use Tensor Cores (mixed precision)
cublasSetMathMode(handle, CUBLAS_TENSOR_OP_MATH);

// FP16 GEMM using Tensor Cores
// Inputs: FP16, Output: FP16 or FP32
cublasGemmEx(handle,
    CUBLAS_OP_N, CUBLAS_OP_N,
    N, M, K,
    &alpha,
    d_B, CUDA_R_16F, N,        // FP16 input
    d_A, CUDA_R_16F, K,        // FP16 input
    &beta,
    d_C, CUDA_R_16F, N,        // FP16 output
    CUDA_R_32F,                // FP32 compute
    CUBLAS_GEMM_DEFAULT_TENSOR_OP);
```

### cuBLASLt - Advanced Interface

cuBLASLt provides more control and optimizations:

```cpp
#include <cublasLt.h>

cublasLtHandle_t ltHandle;
cublasLtCreate(&ltHandle);

// Create matrix layouts
cublasLtMatrixLayout_t Adesc, Bdesc, Cdesc;
cublasLtMatrixLayoutCreate(&Adesc, CUDA_R_16F, M, K, M);
cublasLtMatrixLayoutCreate(&Bdesc, CUDA_R_16F, K, N, K);
cublasLtMatrixLayoutCreate(&Cdesc, CUDA_R_16F, M, N, M);

// Create operation descriptor
cublasLtMatmulDesc_t operationDesc;
cublasLtMatmulDescCreate(&operationDesc, CUBLAS_COMPUTE_32F, CUDA_R_32F);

// Find best algorithm
cublasLtMatmulPreference_t preference;
cublasLtMatmulPreferenceCreate(&preference);
cublasLtMatmulPreferenceSetAttribute(preference,
    CUBLASLT_MATMUL_PREF_MAX_WORKSPACE_BYTES,
    &workspaceSize, sizeof(workspaceSize));

cublasLtMatmulHeuristicResult_t heuristic;
int returnedResults;
cublasLtMatmulAlgoGetHeuristic(ltHandle,
    operationDesc, Adesc, Bdesc, Cdesc, Cdesc,
    preference, 1, &heuristic, &returnedResults);

// Execute
cublasLtMatmul(ltHandle,
    operationDesc,
    &alpha,
    d_A, Adesc,
    d_B, Bdesc,
    &beta,
    d_C, Cdesc,
    d_C, Cdesc,
    &heuristic.algo,
    workspace, workspaceSize,
    stream);

// Cleanup
cublasLtDestroy(ltHandle);
```

## TensorRT - Inference Optimization

TensorRT optimizes neural networks for inference deployment.

### TensorRT Optimizations

1. **Layer Fusion**: Combine multiple layers into single kernels
2. **Precision Calibration**: FP16/INT8 quantization
3. **Kernel Auto-tuning**: Select fastest implementation
4. **Dynamic Tensor Memory**: Reduce memory footprint
5. **Multi-Stream Execution**: Parallel inference

### TensorRT Workflow

```
Trained Model (ONNX/PyTorch/TF)
    ↓
TensorRT Builder
    ↓
Optimization
├── Layer fusion
├── Precision calibration (INT8)
├── Kernel auto-tuning
└── Memory optimization
    ↓
Serialized Engine (.plan file)
    ↓
TensorRT Runtime
    ↓
Optimized Inference
```

### TensorRT Example: ResNet50

```python
import tensorrt as trt
import torch
import torch.onnx

# Step 1: Export PyTorch model to ONNX
model = torchvision.models.resnet50(pretrained=True).cuda().eval()
dummy_input = torch.randn(1, 3, 224, 224).cuda()

torch.onnx.export(
    model,
    dummy_input,
    "resnet50.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)

# Step 2: Build TensorRT engine
TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

def build_engine(onnx_file, engine_file, precision="fp16"):
    builder = trt.Builder(TRT_LOGGER)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, TRT_LOGGER)

    # Parse ONNX
    with open(onnx_file, "rb") as f:
        if not parser.parse(f.read()):
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return None

    # Configure builder
    config = builder.create_builder_config()
    config.max_workspace_size = 4 << 30  # 4GB

    if precision == "fp16":
        config.set_flag(trt.BuilderFlag.FP16)
    elif precision == "int8":
        config.set_flag(trt.BuilderFlag.INT8)
        # TODO: Add INT8 calibration

    # Build engine
    engine = builder.build_engine(network, config)

    # Serialize
    with open(engine_file, "wb") as f:
        f.write(engine.serialize())

    return engine

engine = build_engine("resnet50.onnx", "resnet50.plan", precision="fp16")

# Step 3: Run inference
def infer(engine, input_data):
    context = engine.create_execution_context()

    # Allocate buffers
    input_shape = (1, 3, 224, 224)
    output_shape = (1, 1000)

    d_input = cuda.mem_alloc(input_data.nbytes)
    d_output = cuda.mem_alloc(np.prod(output_shape) * 4)  # FP32 output

    bindings = [int(d_input), int(d_output)]
    stream = cuda.Stream()

    # Transfer input data
    cuda.memcpy_htod_async(d_input, input_data, stream)

    # Execute
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)

    # Transfer output
    output = np.empty(output_shape, dtype=np.float32)
    cuda.memcpy_dtoh_async(output, d_output, stream)
    stream.synchronize()

    return output

# TODO: Benchmark TensorRT vs PyTorch inference
```

### INT8 Quantization with Calibration

```python
# INT8 calibration for TensorRT
class Int8Calibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calibration_dataset, cache_file):
        trt.IInt8EntropyCalibrator2.__init__(self)
        self.dataset = calibration_dataset
        self.cache_file = cache_file
        self.current_index = 0

        # Allocate GPU memory for batch
        self.batch_size = 32
        self.device_input = cuda.mem_alloc(self.batch_size * 3 * 224 * 224 * 4)

    def get_batch_size(self):
        return self.batch_size

    def get_batch(self, names):
        if self.current_index >= len(self.dataset):
            return None

        batch = self.dataset[self.current_index:self.current_index + self.batch_size]
        cuda.memcpy_htod(self.device_input, batch)
        self.current_index += self.batch_size

        return [int(self.device_input)]

    def read_calibration_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                return f.read()
        return None

    def write_calibration_cache(self, cache):
        with open(self.cache_file, "wb") as f:
            f.write(cache)

# Use calibrator in builder
config.int8_calibrator = Int8Calibrator(calibration_dataset, "calibration.cache")
```

### TensorRT Best Practices

1. **Use ONNX** for model portability
2. **Enable FP16** for 2-3x speedup on Tensor Cores
3. **Use INT8** for 4-5x speedup with minimal accuracy loss
4. **Dynamic shapes** for variable batch sizes
5. **Profile layers** to identify bottlenecks
6. **Serialize engines** to avoid rebuilding

## cuSPARSE and cuFFT

### cuSPARSE - Sparse Matrix Operations

cuSPARSE accelerates sparse linear algebra:

```cpp
#include <cusparse.h>

// Sparse matrix-vector multiplication
cusparseHandle_t handle;
cusparseCreate(&handle);

// Create sparse matrix (CSR format)
cusparseSpMatDescr_t matA;
cusparseCreateCsr(&matA,
    num_rows, num_cols, nnz,
    d_csrRowPtr, d_csrColInd, d_csrValues,
    CUSPARSE_INDEX_32I, CUSPARSE_INDEX_32I,
    CUSPARSE_INDEX_BASE_ZERO, CUDA_R_32F);

// Create dense vectors
cusparseDnVecDescr_t vecX, vecY;
cusparseCreateDnVec(&vecX, num_cols, d_x, CUDA_R_32F);
cusparseCreateDnVec(&vecY, num_rows, d_y, CUDA_R_32F);

// Compute y = alpha * A * x + beta * y
float alpha = 1.0f, beta = 0.0f;
size_t bufferSize;
cusparseSpMV_bufferSize(handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
    &alpha, matA, vecX, &beta, vecY, CUDA_R_32F,
    CUSPARSE_SPMV_ALG_DEFAULT, &bufferSize);

void* buffer;
cudaMalloc(&buffer, bufferSize);

cusparseSpMV(handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
    &alpha, matA, vecX, &beta, vecY, CUDA_R_32F,
    CUSPARSE_SPMV_ALG_DEFAULT, buffer);

cusparseDestroy(handle);
```

**Use Cases:**
- Sparse attention mechanisms
- Graph neural networks
- Pruned model inference
- Sparse linear layers

### cuFFT - Fast Fourier Transform

```cpp
#include <cufft.h>

// 1D FFT
cufftHandle plan;
cufftPlan1d(&plan, N, CUFFT_C2C, 1);

// Execute forward FFT
cufftComplex* d_input;
cufftComplex* d_output;
cufftExecC2C(plan, d_input, d_output, CUFFT_FORWARD);

// Execute inverse FFT
cufftExecC2C(plan, d_output, d_input, CUFFT_INVERSE);

cufftDestroy(plan);

// TODO: Implement FFT-based convolution
```

**Use Cases:**
- Signal processing
- FFT-based convolutions
- Spectral methods

## Thrust - High-Level Parallel Algorithms

Thrust provides STL-like interface for GPU programming:

```cpp
#include <thrust/device_vector.h>
#include <thrust/sort.h>
#include <thrust/reduce.h>
#include <thrust/transform.h>

// Sorting
thrust::device_vector<float> d_vec(1000000);
thrust::sort(d_vec.begin(), d_vec.end());

// Reduction (sum)
float sum = thrust::reduce(d_vec.begin(), d_vec.end(), 0.0f, thrust::plus<float>());

// Transform (element-wise operation)
thrust::transform(d_vec.begin(), d_vec.end(), d_vec.begin(),
                  [] __device__ (float x) { return x * x; });  // Square elements

// Scan (prefix sum)
thrust::device_vector<float> d_output(1000000);
thrust::inclusive_scan(d_vec.begin(), d_vec.end(), d_output.begin());

// Custom functor
struct relu_functor {
    __device__ float operator()(float x) const {
        return fmaxf(0.0f, x);
    }
};

thrust::transform(d_vec.begin(), d_vec.end(), d_vec.begin(), relu_functor());
```

**Use Cases:**
- Data preprocessing
- Custom operations without writing CUDA kernels
- Prototyping GPU algorithms

## NCCL - Multi-GPU Communication

NCCL (NVIDIA Collective Communications Library) provides optimized collective operations for multi-GPU training.

### NCCL Operations

- **All-Reduce**: Sum values across all GPUs, result on all GPUs
- **Broadcast**: Send data from one GPU to all others
- **Reduce**: Sum values across all GPUs, result on one GPU
- **All-Gather**: Gather data from all GPUs to all GPUs
- **Reduce-Scatter**: Reduce and scatter results

### NCCL Example

```cpp
#include <nccl.h>

// Initialize NCCL
int nGPUs = 4;
ncclComm_t comms[nGPUs];
int devs[nGPUs] = {0, 1, 2, 3};

ncclCommInitAll(comms, nGPUs, devs);

// Allocate data on each GPU
float** sendbuff = (float**)malloc(nGPUs * sizeof(float*));
float** recvbuff = (float**)malloc(nGPUs * sizeof(float*));
cudaStream_t streams[nGPUs];

for (int i = 0; i < nGPUs; i++) {
    cudaSetDevice(i);
    cudaMalloc(&sendbuff[i], size * sizeof(float));
    cudaMalloc(&recvbuff[i], size * sizeof(float));
    cudaStreamCreate(&streams[i]);
}

// All-reduce across GPUs (sum gradients)
for (int i = 0; i < nGPUs; i++) {
    cudaSetDevice(i);
    ncclAllReduce(sendbuff[i], recvbuff[i], size, ncclFloat, ncclSum,
                  comms[i], streams[i]);
}

// Wait for completion
for (int i = 0; i < nGPUs; i++) {
    cudaSetDevice(i);
    cudaStreamSynchronize(streams[i]);
}

// Cleanup
for (int i = 0; i < nGPUs; i++) {
    ncclCommDestroy(comms[i]);
}
```

### NCCL with PyTorch

```python
import torch
import torch.distributed as dist

# Initialize process group with NCCL backend
dist.init_process_group(backend='nccl', init_method='env://')

# Distributed data parallel
model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])

# NCCL handles gradient synchronization automatically
loss.backward()  # Gradients are all-reduced across GPUs
optimizer.step()

# Manual all-reduce
tensor = torch.randn(100, 100).cuda()
dist.all_reduce(tensor, op=dist.ReduceOp.SUM)

# TODO: Implement custom distributed training loop with NCCL
```

## Integration with ML Frameworks

### PyTorch Backend

PyTorch uses CUDA libraries internally:

```python
import torch

# Matrix multiplication uses cuBLAS
a = torch.randn(1000, 1000).cuda()
b = torch.randn(1000, 1000).cuda()
c = torch.mm(a, b)  # Calls cublasSgemm

# Convolution uses cuDNN
conv = torch.nn.Conv2d(3, 64, kernel_size=3).cuda()
input = torch.randn(32, 3, 224, 224).cuda()
output = conv(input)  # Calls cudnnConvolutionForward

# Check cuDNN status
print(torch.backends.cudnn.enabled)     # Should be True
print(torch.backends.cudnn.version())   # cuDNN version
```

### TensorFlow Backend

```python
import tensorflow as tf

# TensorFlow also uses cuDNN and cuBLAS
physical_devices = tf.config.list_physical_devices('GPU')
print(f"GPUs available: {len(physical_devices)}")

# Matrix multiplication
a = tf.random.normal([1000, 1000])
b = tf.random.normal([1000, 1000])
c = tf.matmul(a, b)  # Uses cuBLAS

# Convolution
conv = tf.keras.layers.Conv2D(64, kernel_size=3)
input = tf.random.normal([32, 224, 224, 3])
output = conv(input)  # Uses cuDNN
```

### Custom Operations

Integrating custom CUDA kernels with PyTorch:

```cpp
// custom_ops.cu
#include <torch/extension.h>

__global__ void relu_kernel(const float* input, float* output, int size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size) {
        output[idx] = fmaxf(0.0f, input[idx]);
    }
}

torch::Tensor relu_cuda(torch::Tensor input) {
    auto output = torch::empty_like(input);
    int threads = 256;
    int blocks = (input.numel() + threads - 1) / threads;

    relu_kernel<<<blocks, threads>>>(
        input.data_ptr<float>(),
        output.data_ptr<float>(),
        input.numel()
    );

    return output;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("relu_cuda", &relu_cuda, "ReLU CUDA");
}
```

```python
# setup.py
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name='custom_ops',
    ext_modules=[
        CUDAExtension('custom_ops', [
            'custom_ops.cu',
        ])
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)

# Install and use
# python setup.py install
import custom_ops
output = custom_ops.relu_cuda(input_tensor)
```

## Summary

Key takeaways from CUDA libraries:

1. **cuDNN**: Provides optimized neural network primitives used by all frameworks
2. **cuBLAS**: Essential for matrix operations and transformers
3. **TensorRT**: Optimizes models for production inference (2-10x speedup)
4. **NCCL**: Enables efficient multi-GPU training
5. **Leverage existing libraries** instead of writing custom kernels when possible
6. **Understand framework backends** to debug performance issues

## Hands-on Exercise

Compare performance of cuBLAS vs. naive matrix multiplication:

```bash
# Compile and run CUDA samples
cd /usr/local/cuda/samples/7_CUDALibraries
make

# Run cuBLAS sample
./simpleCUBLAS

# Profile with nvprof
nvprof ./simpleCUBLAS
```

## Further Reading

- cuDNN Developer Guide: https://docs.nvidia.com/deeplearning/cudnn/
- cuBLAS Documentation: https://docs.nvidia.com/cuda/cublas/
- TensorRT Developer Guide: https://docs.nvidia.com/deeplearning/tensorrt/
- NCCL Documentation: https://docs.nvidia.com/deeplearning/nccl/

---

**Next Lecture**: GPU Profiling with Nsight Tools
