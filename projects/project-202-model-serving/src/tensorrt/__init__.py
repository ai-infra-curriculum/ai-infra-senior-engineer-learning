"""
TensorRT Optimization Module

This module provides utilities for converting PyTorch/ONNX models to TensorRT
and running optimized inference with TensorRT engines.

TODO for students:
- Understand TensorRT optimization techniques (FP16, INT8 quantization)
- Implement dynamic shape handling for variable batch sizes
- Add calibration for INT8 quantization
- Implement engine caching and versioning
"""

from .convert_to_tensorrt import (
    convert_onnx_to_tensorrt,
    convert_pytorch_to_tensorrt,
    TensorRTConverter,
)
from .tensorrt_inference import (
    TensorRTInference,
    TensorRTPredictor,
    load_engine,
)
from .optimize import (
    optimize_for_fp16,
    optimize_for_int8,
    build_engine,
    TensorRTOptimizer,
)

__all__ = [
    # Conversion
    "convert_onnx_to_tensorrt",
    "convert_pytorch_to_tensorrt",
    "TensorRTConverter",
    # Inference
    "TensorRTInference",
    "TensorRTPredictor",
    "load_engine",
    # Optimization
    "optimize_for_fp16",
    "optimize_for_int8",
    "build_engine",
    "TensorRTOptimizer",
]
