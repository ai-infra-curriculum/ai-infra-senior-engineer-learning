#!/bin/bash
# Convert PyTorch models to TensorRT format
# TODO for students: Add INT8 calibration, add dynamic shapes, support multiple model formats

set -euo pipefail

echo "========================================="
echo "Model Conversion to TensorRT"
echo "========================================="

# Configuration
INPUT_MODEL="${1:-models/resnet50.pth}"
OUTPUT_DIR="${2:-models/tensorrt}"
PRECISION="${3:-fp16}"  # fp32, fp16, or int8

mkdir -p "$OUTPUT_DIR"

echo "Converting model: $INPUT_MODEL"
echo "Precision: $PRECISION"
echo "Output directory: $OUTPUT_DIR"

# Convert to ONNX first
echo -e "\n[1/2] Converting to ONNX..."
python src/tensorrt/convert_to_tensorrt.py \
  --input "$INPUT_MODEL" \
  --output "$OUTPUT_DIR/model.onnx" \
  --format onnx

# Convert ONNX to TensorRT
echo -e "\n[2/2] Converting ONNX to TensorRT..."
python src/tensorrt/optimize.py \
  --input "$OUTPUT_DIR/model.onnx" \
  --output "$OUTPUT_DIR/model_${PRECISION}.engine" \
  --precision "$PRECISION" \
  --batch-size 1 \
  --verbose

echo -e "\n========================================="
echo "Conversion complete!"
echo "TensorRT engine: $OUTPUT_DIR/model_${PRECISION}.engine"
echo "========================================="
