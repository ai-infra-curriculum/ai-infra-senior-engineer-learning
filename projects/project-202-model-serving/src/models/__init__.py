"""
Model Abstraction Layer

This module provides base model interfaces and implementations for different
model types (CNNs, LLMs) with unified serving API.

TODO for students:
- Implement model versioning and A/B testing
- Add model warmup and preloading
- Implement model fallback strategies
- Add support for multi-model serving
- Implement model health checks
"""

from .base_model import (
    BaseModel,
    ModelMetadata,
    InferenceRequest,
    InferenceResponse,
)
from .cnn_model import (
    CNNModel,
    ImageClassificationModel,
    ObjectDetectionModel,
)
from .llm_model import (
    LLMModel,
    TextGenerationModel,
    ChatModel,
)

__all__ = [
    # Base classes
    "BaseModel",
    "ModelMetadata",
    "InferenceRequest",
    "InferenceResponse",
    # CNN Models
    "CNNModel",
    "ImageClassificationModel",
    "ObjectDetectionModel",
    # LLM Models
    "LLMModel",
    "TextGenerationModel",
    "ChatModel",
]
