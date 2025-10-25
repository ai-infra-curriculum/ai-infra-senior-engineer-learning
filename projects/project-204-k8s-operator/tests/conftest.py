"""Pytest configuration and fixtures for TrainingJob operator tests.

TODO for students: Add more fixtures for:
- Mock Kubernetes clients
- Test TrainingJob resources
- Mock controllers
- Integration test helpers
"""

import pytest
from typing import Dict, Any
from unittest.mock import MagicMock


@pytest.fixture
def sample_training_job_spec() -> Dict[str, Any]:
    """Sample TrainingJob specification for testing.

    TODO for students: Add more test scenarios:
    - Different frameworks (TensorFlow, JAX)
    - GPU configurations
    - Distributed training setups
    - Custom resources and volumes
    """
    return {
        "framework": "pytorch",
        "image": "pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
        "command": ["python", "-m", "torch.distributed.launch"],
        "args": ["train.py"],
        "replicas": 2,
        "resources": {
            "requests": {"cpu": "2", "memory": "4Gi"},
            "limits": {"cpu": "4", "memory": "8Gi"},
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
        },
    }


@pytest.fixture
def sample_training_job(sample_training_job_spec) -> Dict[str, Any]:
    """Complete TrainingJob resource for testing.

    Returns:
        TrainingJob resource dict
    """
    return {
        "apiVersion": "mlplatform.example.com/v1alpha1",
        "kind": "TrainingJob",
        "metadata": {
            "name": "test-job",
            "namespace": "default",
            "uid": "test-uid-123",
        },
        "spec": sample_training_job_spec,
        "status": {
            "phase": "Pending",
            "conditions": [],
        },
    }


@pytest.fixture
def mock_k8s_client():
    """Mock Kubernetes client for testing.

    TODO for students: Implement proper mock K8s client with:
    - Mock API methods (create, get, list, delete)
    - Mock watch functionality
    - Mock status updates
    """
    mock = MagicMock()
    mock.list_namespaced_custom_object.return_value = {"items": []}
    mock.get_namespaced_custom_object.return_value = {}
    return mock


@pytest.fixture
def mock_job_controller():
    """Mock JobController for testing.

    TODO for students: Add more mock methods as needed
    """
    mock = MagicMock()
    mock.reconcile.return_value = True
    return mock


@pytest.fixture
def mock_checkpoint_controller():
    """Mock CheckpointController for testing."""
    mock = MagicMock()
    mock.should_checkpoint.return_value = False
    mock.list_checkpoints.return_value = []
    return mock
