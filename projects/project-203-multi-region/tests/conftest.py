"""Pytest configuration and fixtures for multi-region testing.

TODO for students: Add more fixtures for specific test scenarios:
- Mock cloud provider clients
- Database fixtures with test data
- Kubernetes client mocks
- Network latency simulation
"""

import os
from typing import Dict, List
from unittest.mock import MagicMock, Mock

import pytest


# ==============================================================================
# CONFIGURATION FIXTURES
# ==============================================================================

@pytest.fixture
def test_regions() -> List[str]:
    """Provide list of test regions.

    TODO for students: Add more regions or customize based on test needs
    """
    return ["us-east-1", "eu-west-1", "ap-southeast-1"]


@pytest.fixture
def primary_region() -> str:
    """Provide primary region for testing."""
    return "us-east-1"


@pytest.fixture
def test_config() -> Dict[str, any]:
    """Provide test configuration dictionary.

    TODO for students: Expand with more configuration options
    """
    return {
        "regions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
        "primary_region": "us-east-1",
        "replication_strategy": "active-active",
        "failover_enabled": True,
        "health_check_interval": 30,
    }


# ==============================================================================
# REPLICATION FIXTURES
# ==============================================================================

@pytest.fixture
def mock_model_replicator():
    """Mock ModelReplicator for testing.

    TODO for students: Add more methods and behaviors as needed
    """
    replicator = MagicMock()
    replicator.replicate_model.return_value = True
    replicator.verify_replication.return_value = True
    replicator.get_replication_status.return_value = "healthy"
    return replicator


@pytest.fixture
def mock_data_synchronizer():
    """Mock DataSynchronizer for testing.

    TODO for students: Add sync strategies and error scenarios
    """
    synchronizer = MagicMock()
    synchronizer.sync_data.return_value = {"status": "success", "records_synced": 100}
    synchronizer.verify_consistency.return_value = True
    return synchronizer


# ==============================================================================
# MONITORING FIXTURES
# ==============================================================================

@pytest.fixture
def mock_metrics_collector():
    """Mock MetricsCollector for testing.

    TODO for students: Add different metric types and aggregations
    """
    collector = MagicMock()
    collector.collect_metrics.return_value = {
        "latency_ms": 50,
        "error_rate": 0.01,
        "throughput_rps": 1000,
    }
    return collector


@pytest.fixture
def sample_metrics() -> Dict[str, float]:
    """Provide sample metrics data for testing.

    TODO for students: Add more metric types (GPU, memory, network)
    """
    return {
        "cpu_usage_percent": 45.5,
        "memory_usage_mb": 2048,
        "request_latency_ms": 125,
        "error_rate": 0.005,
        "throughput_rps": 850,
    }


# ==============================================================================
# FAILOVER FIXTURES
# ==============================================================================

@pytest.fixture
def mock_failover_controller():
    """Mock FailoverController for testing.

    TODO for students: Add different failover scenarios and states
    """
    controller = MagicMock()
    controller.check_health.return_value = True
    controller.trigger_failover.return_value = {"status": "success", "new_primary": "eu-west-1"}
    controller.rollback_failover.return_value = True
    return controller


@pytest.fixture
def health_check_results() -> Dict[str, Dict]:
    """Provide sample health check results.

    TODO for students: Add unhealthy and degraded states
    """
    return {
        "us-east-1": {"status": "healthy", "latency_ms": 10, "error_rate": 0.001},
        "eu-west-1": {"status": "healthy", "latency_ms": 15, "error_rate": 0.002},
        "ap-southeast-1": {"status": "healthy", "latency_ms": 20, "error_rate": 0.001},
    }


# ==============================================================================
# DEPLOYMENT FIXTURES
# ==============================================================================

@pytest.fixture
def mock_orchestrator():
    """Mock MultiRegionOrchestrator for testing.

    TODO for students: Add deployment strategies and rollback scenarios
    """
    orchestrator = MagicMock()
    orchestrator.deploy.return_value = {"status": "success", "regions": ["us-east-1", "eu-west-1"]}
    orchestrator.rollback.return_value = True
    return orchestrator


@pytest.fixture
def deployment_config() -> Dict[str, any]:
    """Provide deployment configuration.

    TODO for students: Add blue-green and canary deployment configs
    """
    return {
        "strategy": "rolling",
        "max_unavailable": 1,
        "max_surge": 1,
        "health_check_grace_period": 60,
    }


# ==============================================================================
# COST OPTIMIZATION FIXTURES
# ==============================================================================

@pytest.fixture
def mock_cost_optimizer():
    """Mock CostOptimizer for testing.

    TODO for students: Add cost analysis and recommendation scenarios
    """
    optimizer = MagicMock()
    optimizer.analyze_costs.return_value = {
        "total_monthly_cost": 5000,
        "by_region": {
            "us-east-1": 2000,
            "eu-west-1": 1500,
            "ap-southeast-1": 1500,
        },
    }
    optimizer.get_recommendations.return_value = [
        "Consider using spot instances",
        "Reduce idle resources in ap-southeast-1",
    ]
    return optimizer


# ==============================================================================
# CLOUD PROVIDER FIXTURES
# ==============================================================================

@pytest.fixture
def mock_aws_client():
    """Mock AWS client for testing.

    TODO for students: Add specific service mocks (S3, EC2, EKS)
    """
    client = MagicMock()
    client.list_regions.return_value = ["us-east-1", "eu-west-1", "ap-southeast-1"]
    return client


@pytest.fixture
def mock_kubernetes_client():
    """Mock Kubernetes client for testing.

    TODO for students: Add namespace, pod, and service mocks
    """
    client = MagicMock()
    client.list_namespaces.return_value = ["ml-platform", "monitoring"]
    client.get_pods.return_value = [
        {"name": "model-server-1", "status": "Running"},
        {"name": "model-server-2", "status": "Running"},
    ]
    return client


# ==============================================================================
# DATABASE FIXTURES
# ==============================================================================

@pytest.fixture
def mock_database():
    """Mock database connection for testing.

    TODO for students: Add transaction support and query mocking
    """
    db = MagicMock()
    db.execute.return_value = Mock(rowcount=1)
    db.fetchall.return_value = []
    return db


# ==============================================================================
# ENVIRONMENT FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch):
    """Set test environment variables.

    TODO for students: Add more environment variables as needed
    Automatically applied to all tests.
    """
    test_env = {
        "ENVIRONMENT": "testing",
        "REGIONS": "us-east-1,eu-west-1,ap-southeast-1",
        "PRIMARY_REGION": "us-east-1",
        "REPLICATION_ENABLED": "true",
        "DEBUG_MODE": "true",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary configuration file for testing.

    TODO for students: Add different config formats (YAML, TOML)
    """
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"regions": ["us-east-1"], "primary_region": "us-east-1"}')
    return config_file


# ==============================================================================
# TEST MARKERS
# ==============================================================================

def pytest_configure(config):
    """Register custom pytest markers.

    TODO for students: Add more markers for categorizing tests
    """
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "replication: mark test as replication test")
    config.addinivalue_line("markers", "failover: mark test as failover test")
    config.addinivalue_line("markers", "cost: mark test as cost optimization test")
