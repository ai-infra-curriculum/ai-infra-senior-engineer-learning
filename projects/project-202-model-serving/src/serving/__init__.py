"""
Model Serving Infrastructure

This module provides the FastAPI-based serving layer with model management,
request routing, and monitoring.

TODO for students:
- Implement graceful model loading/unloading
- Add request batching and adaptive batching
- Implement circuit breaker pattern
- Add request queuing and priority scheduling
- Implement rate limiting per client
"""

from .main import (
    app,
    create_app,
    start_server,
)
from .model_manager import (
    ModelManager,
    ModelRegistry,
    load_model,
    unload_model,
)
from .router import (
    InferenceRouter,
    route_request,
    ModelSelector,
)

__all__ = [
    # FastAPI app
    "app",
    "create_app",
    "start_server",
    # Model Management
    "ModelManager",
    "ModelRegistry",
    "load_model",
    "unload_model",
    # Routing
    "InferenceRouter",
    "route_request",
    "ModelSelector",
]
