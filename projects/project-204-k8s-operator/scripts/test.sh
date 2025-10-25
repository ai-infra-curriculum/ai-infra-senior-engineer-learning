#!/bin/bash
# Test script for TrainingJob Kubernetes Operator
# This script runs all tests (unit, integration, e2e)
#
# TODO for students: Add:
# - Code coverage reporting
# - Integration tests with real cluster
# - End-to-end tests
# - Performance tests
# - Linting and type checking

set -e

echo "===================================="
echo "TrainingJob Operator Tests"
echo "===================================="

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run unit tests
echo ""
echo "Running unit tests..."
python3 -m pytest tests/ -v

# TODO for students: Run with coverage
# echo ""
# echo "Running tests with coverage..."
# python3 -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# TODO for students: Run linting
# echo ""
# echo "Running linting..."
# python3 -m pylint src/
# python3 -m flake8 src/

# TODO for students: Run type checking
# echo ""
# echo "Running type checking..."
# python3 -m mypy src/

# TODO for students: Run integration tests (if cluster available)
# if kubectl cluster-info &> /dev/null; then
#     echo ""
#     echo "Running integration tests..."
#     python3 -m pytest tests/integration/ -v
# else
#     echo ""
#     echo "Skipping integration tests (no cluster available)"
# fi

# TODO for students: Run end-to-end tests
# echo ""
# echo "Running end-to-end tests..."
# python3 -m pytest tests/e2e/ -v

echo ""
echo "===================================="
echo "All tests passed!"
echo "===================================="
echo ""

# TODO for students: Display coverage report
# echo "Coverage report: htmlcov/index.html"
# echo ""
