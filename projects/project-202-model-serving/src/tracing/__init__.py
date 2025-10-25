"""
Distributed Tracing Module

This module provides Jaeger-based distributed tracing for request tracking
across model serving components.

TODO for students:
- Implement context propagation across services
- Add custom span tags for model metadata
- Implement sampling strategies
- Add tracing for async operations
- Integrate with logging for correlation
"""

from .jaeger_integration import (
    init_tracer,
    get_tracer,
    create_span,
    JaegerConfig,
)
from .span_decorator import (
    trace_function,
    trace_async_function,
    add_span_tags,
    SpanContext,
)

__all__ = [
    # Jaeger Integration
    "init_tracer",
    "get_tracer",
    "create_span",
    "JaegerConfig",
    # Span Decorators
    "trace_function",
    "trace_async_function",
    "add_span_tags",
    "SpanContext",
]
