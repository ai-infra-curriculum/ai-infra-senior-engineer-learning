"""TrainingJob Custom Resource Definition (CRD).

TODO for students: Enhance the CRD with:
- Additional validation rules in OpenAPI schema
- Defaulting webhooks for automatic field population
- Conversion webhooks for version migration
- Printer columns for kubectl output customization
- Short names and categories for better UX
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TrainingJobCRD:
    """TrainingJob Custom Resource Definition.

    TODO for students: Extend with:
    - Multiple API versions (v1alpha1, v1beta1, v1)
    - Subresources (status, scale)
    - Admission webhooks
    - Custom validation logic
    """

    group: str = "mlplatform.example.com"
    version: str = "v1alpha1"
    plural: str = "trainingjobs"
    singular: str = "trainingjob"
    kind: str = "TrainingJob"
    short_names: list = field(default_factory=lambda: ["tj", "trainjob"])
    categories: list = field(default_factory=lambda: ["ml", "ai"])

    @property
    def scope(self) -> str:
        """Resource scope (Namespaced or Cluster)."""
        # TODO for students: Consider when to use Cluster scope
        return "Namespaced"

    def get_crd_manifest(self) -> Dict[str, Any]:
        """Get the complete CRD manifest.

        TODO for students: Add:
        - Conversion strategy for multi-version support
        - Webhook configurations
        - Additional printer columns
        - Validation webhook references

        Returns:
            CRD manifest dict
        """
        return {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": f"{self.plural}.{self.group}",
                "annotations": {
                    "controller-gen.kubebuilder.io/version": "v0.11.0",
                },
            },
            "spec": {
                "group": self.group,
                "names": {
                    "kind": self.kind,
                    "listKind": f"{self.kind}List",
                    "plural": self.plural,
                    "singular": self.singular,
                    "shortNames": self.short_names,
                    "categories": self.categories,
                },
                "scope": self.scope,
                "versions": [
                    {
                        "name": self.version,
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": self._get_openapi_schema()
                        },
                        "subresources": {
                            "status": {},
                            # TODO for students: Add scale subresource
                            # "scale": {
                            #     "specReplicasPath": ".spec.replicas",
                            #     "statusReplicasPath": ".status.replicas",
                            # }
                        },
                        "additionalPrinterColumns": [
                            {
                                "name": "Status",
                                "type": "string",
                                "jsonPath": ".status.phase",
                            },
                            {
                                "name": "Framework",
                                "type": "string",
                                "jsonPath": ".spec.framework",
                            },
                            {
                                "name": "Replicas",
                                "type": "integer",
                                "jsonPath": ".spec.replicas",
                            },
                            {
                                "name": "Age",
                                "type": "date",
                                "jsonPath": ".metadata.creationTimestamp",
                            },
                            # TODO for students: Add more useful columns
                            # - Completion time
                            # - GPU count
                            # - Model name
                        ],
                    }
                ],
            },
        }

    def _get_openapi_schema(self) -> Dict[str, Any]:
        """Get OpenAPI v3 schema for validation.

        TODO for students: Enhance validation with:
        - Pattern validation for strings
        - Enum restrictions for specific fields
        - Minimum/maximum values
        - Required field combinations
        - Custom validation rules

        Returns:
            OpenAPI schema dict
        """
        return {
            "type": "object",
            "properties": {
                "spec": {
                    "type": "object",
                    "required": ["image", "command", "framework"],
                    "properties": {
                        # Framework configuration
                        "framework": {
                            "type": "string",
                            "enum": ["pytorch", "tensorflow", "jax", "mxnet"],
                            "description": "ML framework to use",
                        },
                        "frameworkVersion": {
                            "type": "string",
                            "description": "Framework version",
                            # TODO: Add pattern validation
                            # "pattern": "^\\d+\\.\\d+\\.\\d+$"
                        },
                        # Container configuration
                        "image": {
                            "type": "string",
                            "description": "Container image for training",
                            # TODO: Add pattern for valid image names
                        },
                        "command": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command to run",
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arguments for command",
                        },
                        # Scaling configuration
                        "replicas": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 1,
                            "description": "Number of training replicas",
                        },
                        # Resource requirements
                        "resources": {
                            "type": "object",
                            "properties": {
                                "requests": {
                                    "type": "object",
                                    "additionalProperties": {"type": "string"},
                                },
                                "limits": {
                                    "type": "object",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                        },
                        # Restart policy
                        "restartPolicy": {
                            "type": "string",
                            "enum": ["Never", "OnFailure", "Always"],
                            "default": "OnFailure",
                        },
                        "backoffLimit": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 10,
                            "default": 3,
                        },
                        # Checkpoint configuration
                        "checkpoint": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": True},
                                "interval": {
                                    "type": "integer",
                                    "minimum": 60,
                                    "description": "Checkpoint interval in seconds",
                                },
                                "path": {"type": "string"},
                                "storage": {
                                    "type": "string",
                                    "enum": ["pvc", "s3", "gcs", "azure"],
                                },
                            },
                        },
                        # Monitoring configuration
                        "monitoring": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": True},
                                "port": {
                                    "type": "integer",
                                    "minimum": 1024,
                                    "maximum": 65535,
                                },
                                "path": {"type": "string"},
                            },
                        },
                        # Environment variables
                        "env": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "value": {"type": "string"},
                                },
                                "required": ["name"],
                            },
                        },
                        # TODO for students: Add more fields
                        # - Volume mounts
                        # - Service account
                        # - Node selector
                        # - Tolerations
                        # - Affinity rules
                        # - Security context
                    },
                },
                "status": {
                    "type": "object",
                    "properties": {
                        "phase": {
                            "type": "string",
                            "enum": [
                                "Pending",
                                "Running",
                                "Succeeded",
                                "Failed",
                                "Unknown",
                            ],
                        },
                        "conditions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "status": {"type": "string"},
                                    "reason": {"type": "string"},
                                    "message": {"type": "string"},
                                    "lastTransitionTime": {"type": "string"},
                                },
                                "required": ["type", "status"],
                            },
                        },
                        "startTime": {
                            "type": "string",
                            "format": "date-time",
                        },
                        "completionTime": {
                            "type": "string",
                            "format": "date-time",
                        },
                        "replicas": {"type": "integer"},
                        "readyReplicas": {"type": "integer"},
                        # TODO for students: Add more status fields
                        # - Progress metrics
                        # - Resource usage
                        # - Error messages
                        # - Checkpoint information
                    },
                },
            },
        }


def get_trainingjob_crd() -> Dict[str, Any]:
    """Get TrainingJob CRD manifest.

    TODO for students: Add support for:
    - Dynamic CRD generation based on configuration
    - Multiple versions with conversion
    - Custom validation webhook setup

    Returns:
        CRD manifest dict
    """
    crd = TrainingJobCRD()
    return crd.get_crd_manifest()


def create_sample_trainingjob(
    name: str,
    namespace: str = "default",
    framework: str = "pytorch",
    image: Optional[str] = None,
    replicas: int = 1,
) -> Dict[str, Any]:
    """Create a sample TrainingJob resource.

    TODO for students: Extend with more configuration options

    Args:
        name: Job name
        namespace: Kubernetes namespace
        framework: ML framework
        image: Container image (uses default if None)
        replicas: Number of replicas

    Returns:
        TrainingJob resource dict
    """
    from .defaults import get_default_image, get_default_command

    if image is None:
        image = get_default_image(framework)

    return {
        "apiVersion": f"{TrainingJobCRD().group}/{TrainingJobCRD().version}",
        "kind": "TrainingJob",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "framework": framework,
            "image": image,
            "command": get_default_command(framework),
            "replicas": replicas,
            "restartPolicy": "OnFailure",
            "backoffLimit": 3,
            "resources": {
                "requests": {
                    "cpu": "2",
                    "memory": "4Gi",
                },
                "limits": {
                    "cpu": "4",
                    "memory": "8Gi",
                },
            },
            "checkpoint": {
                "enabled": True,
                "interval": 300,
                "path": "/checkpoints",
                "storage": "pvc",
            },
            "monitoring": {
                "enabled": True,
                "port": 9090,
                "path": "/metrics",
            },
        },
    }
