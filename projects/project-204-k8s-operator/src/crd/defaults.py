"""Default values for TrainingJob CRD.

TODO for students: Add more sophisticated defaults:
- Auto-detect GPU requirements
- Set resource limits based on node capacity
- Configure checkpointing defaults
"""

from typing import Dict, Any
from copy import deepcopy


# Default configuration for training jobs
DEFAULT_TRAINING_CONFIG = {
    "replicas": 1,
    "restartPolicy": "OnFailure",
    "backoffLimit": 3,
    "resources": {
        "requests": {
            "cpu": "1",
            "memory": "2Gi",
        },
        "limits": {
            "cpu": "2",
            "memory": "4Gi",
        },
    },
    "checkpoint": {
        "enabled": True,
        "interval": 300,  # seconds
        "path": "/checkpoints",
    },
    "monitoring": {
        "enabled": True,
        "port": 9090,
    },
}


def apply_defaults(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to a TrainingJob spec.

    TODO for students: Implement intelligent defaults based on:
    - Detected framework (PyTorch, TensorFlow)
    - Cluster capacity
    - User quotas

    Args:
        spec: TrainingJob spec dict

    Returns:
        Spec with defaults applied
    """
    result = deepcopy(spec)

    # Apply top-level defaults
    if "replicas" not in result:
        result["replicas"] = DEFAULT_TRAINING_CONFIG["replicas"]

    if "restartPolicy" not in result:
        result["restartPolicy"] = DEFAULT_TRAINING_CONFIG["restartPolicy"]

    if "backoffLimit" not in result:
        result["backoffLimit"] = DEFAULT_TRAINING_CONFIG["backoffLimit"]

    # Apply resource defaults
    if "resources" not in result:
        result["resources"] = deepcopy(DEFAULT_TRAINING_CONFIG["resources"])
    else:
        if "requests" not in result["resources"]:
            result["resources"]["requests"] = deepcopy(
                DEFAULT_TRAINING_CONFIG["resources"]["requests"]
            )
        if "limits" not in result["resources"]:
            result["resources"]["limits"] = deepcopy(
                DEFAULT_TRAINING_CONFIG["resources"]["limits"]
            )

    # Apply checkpoint defaults
    if "checkpoint" not in result:
        result["checkpoint"] = deepcopy(DEFAULT_TRAINING_CONFIG["checkpoint"])

    # Apply monitoring defaults
    if "monitoring" not in result:
        result["monitoring"] = deepcopy(DEFAULT_TRAINING_CONFIG["monitoring"])

    # TODO for students: Add GPU defaults if GPUs requested
    # if "nvidia.com/gpu" in result.get("resources", {}).get("requests", {}):
    #     result["gpuConfig"] = {...}

    return result


def get_default_image(framework: str = "pytorch") -> str:
    """Get default container image for a framework.

    TODO for students: Maintain a registry of approved images

    Args:
        framework: ML framework name

    Returns:
        Default image URI
    """
    images = {
        "pytorch": "pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
        "tensorflow": "tensorflow/tensorflow:2.14.0-gpu",
        "jax": "gcr.io/deeplearning-platform-release/jax-gpu:latest",
    }

    return images.get(framework, images["pytorch"])


def get_default_command(framework: str = "pytorch") -> list:
    """Get default command for a framework.

    TODO for students: Customize based on distributed training setup

    Args:
        framework: ML framework name

    Returns:
        Default command list
    """
    commands = {
        "pytorch": ["python", "-m", "torch.distributed.launch"],
        "tensorflow": ["python", "train.py"],
        "jax": ["python", "train.py"],
    }

    return commands.get(framework, ["python", "train.py"])
