"""Pytest configuration and fixtures."""

import pytest
import torch

@pytest.fixture
def device():
    """Get device for testing."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

# TODO: Add more fixtures
