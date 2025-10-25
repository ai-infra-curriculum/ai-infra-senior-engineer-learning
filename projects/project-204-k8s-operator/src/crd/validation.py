"""Validation logic for TrainingJob resources.

TODO for students: Add advanced validation:
- Cross-field validation (e.g., GPU requests match framework)
- Quota checking against cluster capacity
- Framework-specific validation rules
- Resource limit validation (requests <= limits)
- Storage path validation
- Network policy validation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


class ValidationError(Exception):
    """Exception raised for TrainingJob validation errors.

    TODO for students: Extend with:
    - Error codes for programmatic handling
    - Structured error details
    - Suggestions for fixing errors
    - Severity levels (warning vs error)
    """

    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize validation error.

        Args:
            message: Error message
            field: Optional field path that caused the error
        """
        self.field = field
        if field:
            message = f"Validation error in field '{field}': {message}"
        super().__init__(message)


@dataclass
class ValidationResult:
    """Result of validation operation.

    TODO for students: Add:
    - Warning messages (non-blocking issues)
    - Suggestions for improvement
    - Performance predictions based on config
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str, field: Optional[str] = None) -> None:
        """Add an error message.

        Args:
            message: Error message
            field: Optional field path
        """
        if field:
            message = f"{field}: {message}"
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str, field: Optional[str] = None) -> None:
        """Add a warning message.

        Args:
            message: Warning message
            field: Optional field path
        """
        if field:
            message = f"{field}: {message}"
        self.warnings.append(message)


def validate_training_job(spec: Dict[str, Any]) -> ValidationResult:
    """Validate a TrainingJob specification.

    TODO for students: Implement comprehensive validation:
    - Call all validation helper functions
    - Aggregate all errors and warnings
    - Add framework-specific validation
    - Validate against cluster policies

    Args:
        spec: TrainingJob spec dict

    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult(is_valid=True)

    # Validate required fields
    _validate_required_fields(spec, result)

    # Validate framework configuration
    _validate_framework(spec, result)

    # Validate container configuration
    _validate_container(spec, result)

    # Validate resource configuration
    _validate_resources(spec, result)

    # Validate checkpoint configuration
    if "checkpoint" in spec:
        _validate_checkpoint(spec["checkpoint"], result)

    # Validate monitoring configuration
    if "monitoring" in spec:
        _validate_monitoring(spec["monitoring"], result)

    # Validate replica configuration
    _validate_replicas(spec, result)

    # TODO for students: Add more validation
    # - Volume configuration
    # - Network policies
    # - Security contexts
    # - Service accounts
    # - Node affinity

    return result


def _validate_required_fields(spec: Dict[str, Any], result: ValidationResult) -> None:
    """Validate required fields are present.

    TODO for students: Make required fields configurable

    Args:
        spec: TrainingJob spec
        result: ValidationResult to update
    """
    required_fields = ["image", "command", "framework"]

    for field in required_fields:
        if field not in spec or not spec[field]:
            result.add_error(f"Required field missing or empty", field=field)


def _validate_framework(spec: Dict[str, Any], result: ValidationResult) -> None:
    """Validate framework configuration.

    TODO for students: Add framework version compatibility checks

    Args:
        spec: TrainingJob spec
        result: ValidationResult to update
    """
    if "framework" not in spec:
        return

    framework = spec["framework"]
    supported_frameworks = ["pytorch", "tensorflow", "jax", "mxnet"]

    if framework not in supported_frameworks:
        result.add_error(
            f"Unsupported framework '{framework}'. "
            f"Supported: {', '.join(supported_frameworks)}",
            field="framework",
        )

    # TODO for students: Validate framework version
    # if "frameworkVersion" in spec:
    #     version = spec["frameworkVersion"]
    #     if not _is_valid_version(version):
    #         result.add_error(f"Invalid version format: {version}")


def _validate_container(spec: Dict[str, Any], result: ValidationResult) -> None:
    """Validate container configuration.

    TODO for students: Add:
    - Image registry validation
    - Image tag validation (avoid 'latest' in prod)
    - Command/args validation
    - Environment variable validation

    Args:
        spec: TrainingJob spec
        result: ValidationResult to update
    """
    if "image" not in spec:
        return

    image = spec["image"]

    # Basic validation
    if not image or not isinstance(image, str):
        result.add_error("Image must be a non-empty string", field="image")
        return

    # TODO for students: Add stricter validation
    # - Validate image name format
    # - Check if using 'latest' tag (warning)
    # - Validate registry accessibility

    if "command" in spec and not isinstance(spec["command"], list):
        result.add_error("Command must be a list of strings", field="command")


def _validate_resources(spec: Dict[str, Any], result: ValidationResult) -> None:
    """Validate resource requirements.

    TODO for students: Add:
    - Validation that requests <= limits
    - GPU resource validation
    - Memory/CPU format validation
    - Quota checking

    Args:
        spec: TrainingJob spec
        result: ValidationResult to update
    """
    if "resources" not in spec:
        result.add_warning("No resource requirements specified", field="resources")
        return

    resources = spec["resources"]

    # Validate structure
    if not isinstance(resources, dict):
        result.add_error("Resources must be a dict", field="resources")
        return

    # Check for requests and limits
    if "requests" in resources:
        _validate_resource_dict(resources["requests"], "resources.requests", result)

    if "limits" in resources:
        _validate_resource_dict(resources["limits"], "resources.limits", result)

    # TODO for students: Validate requests <= limits
    # if "requests" in resources and "limits" in resources:
    #     _validate_requests_vs_limits(resources["requests"], resources["limits"], result)


def _validate_resource_dict(
    resource_dict: Any, field: str, result: ValidationResult
) -> None:
    """Validate a resource dictionary (requests or limits).

    TODO for students: Add quantity parsing and validation

    Args:
        resource_dict: Resource dict
        field: Field name for error messages
        result: ValidationResult to update
    """
    if not isinstance(resource_dict, dict):
        result.add_error("Must be a dict", field=field)
        return

    # TODO for students: Validate resource quantities
    # - CPU: "1", "100m", etc.
    # - Memory: "1Gi", "512Mi", etc.
    # - GPU: integer values


def _validate_checkpoint(checkpoint: Dict[str, Any], result: ValidationResult) -> None:
    """Validate checkpoint configuration.

    TODO for students: Add:
    - Storage backend validation
    - Path format validation
    - Interval reasonableness checks
    - PVC existence validation

    Args:
        checkpoint: Checkpoint config
        result: ValidationResult to update
    """
    if not isinstance(checkpoint, dict):
        result.add_error("Checkpoint must be a dict", field="checkpoint")
        return

    if checkpoint.get("enabled") and "path" not in checkpoint:
        result.add_error("Checkpoint path required when enabled", field="checkpoint.path")

    if "interval" in checkpoint:
        interval = checkpoint["interval"]
        if not isinstance(interval, int) or interval < 60:
            result.add_error(
                "Checkpoint interval must be at least 60 seconds",
                field="checkpoint.interval",
            )

    if "storage" in checkpoint:
        storage = checkpoint["storage"]
        valid_storage = ["pvc", "s3", "gcs", "azure"]
        if storage not in valid_storage:
            result.add_error(
                f"Invalid storage backend: {storage}. "
                f"Valid: {', '.join(valid_storage)}",
                field="checkpoint.storage",
            )


def _validate_monitoring(monitoring: Dict[str, Any], result: ValidationResult) -> None:
    """Validate monitoring configuration.

    TODO for students: Add:
    - Port conflict detection
    - Metrics endpoint validation
    - Prometheus compatibility checks

    Args:
        monitoring: Monitoring config
        result: ValidationResult to update
    """
    if not isinstance(monitoring, dict):
        result.add_error("Monitoring must be a dict", field="monitoring")
        return

    if "port" in monitoring:
        port = monitoring["port"]
        if not isinstance(port, int) or not (1024 <= port <= 65535):
            result.add_error(
                "Monitoring port must be between 1024 and 65535",
                field="monitoring.port",
            )


def _validate_replicas(spec: Dict[str, Any], result: ValidationResult) -> None:
    """Validate replica configuration.

    TODO for students: Add:
    - Distributed training validation
    - Replica count vs cluster capacity check
    - Framework-specific replica requirements

    Args:
        spec: TrainingJob spec
        result: ValidationResult to update
    """
    if "replicas" not in spec:
        return

    replicas = spec["replicas"]

    if not isinstance(replicas, int):
        result.add_error("Replicas must be an integer", field="replicas")
        return

    if replicas < 1:
        result.add_error("Replicas must be at least 1", field="replicas")

    if replicas > 100:
        result.add_warning(
            f"High replica count ({replicas}) may exceed cluster capacity",
            field="replicas",
        )

    # TODO for students: Framework-specific validation
    # - PyTorch distributed training requires specific replica counts
    # - TensorFlow parameter server setup
    # - Horovod ring allreduce requirements


def validate_status_update(
    current_status: Dict[str, Any], new_status: Dict[str, Any]
) -> ValidationResult:
    """Validate a status update.

    TODO for students: Implement status transition validation:
    - Validate phase transitions are legal
    - Check condition types are valid
    - Ensure timestamps are monotonic
    - Validate replica counts

    Args:
        current_status: Current status
        new_status: New status to apply

    Returns:
        ValidationResult
    """
    result = ValidationResult(is_valid=True)

    # TODO for students: Implement status validation logic
    # - Check phase transition is valid (e.g., can't go from Succeeded to Running)
    # - Validate condition updates
    # - Check timestamp ordering

    return result
