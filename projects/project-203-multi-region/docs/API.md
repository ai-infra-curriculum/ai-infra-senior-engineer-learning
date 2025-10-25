# Multi-Region ML Platform API Documentation

> **TODO for students**: Expand this API documentation with actual endpoint examples, request/response schemas, and authentication details for your implementation.

## Overview

This document describes the API endpoints for the multi-region ML platform. The platform provides APIs for:
- Model serving and inference
- Cross-region replication management
- Health monitoring and metrics
- Deployment orchestration
- Cost tracking

## Base URLs

### Global Endpoint
```
https://ml-platform.example.com/api/v1
```

### Regional Endpoints
```
https://us-east-1.ml-platform.example.com/api/v1
https://eu-west-1.ml-platform.example.com/api/v1
https://ap-southeast-1.ml-platform.example.com/api/v1
```

## Authentication

**TODO for students**: Implement authentication using one of:
- API Keys
- JWT tokens
- OAuth 2.0
- Service accounts

```http
Authorization: Bearer <token>
```

## Model Serving APIs

### POST /models/{model_id}/predict

Make a prediction using a deployed model.

**Request:**
```json
{
  "inputs": [
    [1.0, 2.0, 3.0, 4.0]
  ],
  "parameters": {
    "batch_size": 1,
    "timeout_ms": 5000
  }
}
```

**Response:**
```json
{
  "predictions": [0.95],
  "model_id": "model-v1.0.0",
  "model_version": "1.0.0",
  "latency_ms": 45,
  "region": "us-east-1"
}
```

**TODO for students**: Implement batch prediction support and async prediction APIs.

## Replication APIs

### POST /replication/models

Replicate a model to target regions.

**Request:**
```json
{
  "model_id": "model-v1.0.0",
  "source_region": "us-east-1",
  "target_regions": ["eu-west-1", "ap-southeast-1"],
  "verify_checksum": true
}
```

**Response:**
```json
{
  "replication_id": "repl-12345",
  "status": "in_progress",
  "target_regions": ["eu-west-1", "ap-southeast-1"],
  "estimated_completion": "2024-01-15T10:30:00Z"
}
```

### GET /replication/{replication_id}/status

Check replication status.

**Response:**
```json
{
  "replication_id": "repl-12345",
  "status": "completed",
  "results": [
    {
      "region": "eu-west-1",
      "status": "completed",
      "bytes_transferred": 1073741824,
      "duration_seconds": 120
    },
    {
      "region": "ap-southeast-1",
      "status": "completed",
      "bytes_transferred": 1073741824,
      "duration_seconds": 150
    }
  ]
}
```

**TODO for students**: Add endpoints for:
- Data synchronization status
- Configuration sync
- Rollback operations

## Health & Monitoring APIs

### GET /health

Global health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "regions": {
    "us-east-1": {
      "status": "healthy",
      "latency_ms": 10,
      "error_rate": 0.001
    },
    "eu-west-1": {
      "status": "healthy",
      "latency_ms": 15,
      "error_rate": 0.002
    },
    "ap-southeast-1": {
      "status": "degraded",
      "latency_ms": 250,
      "error_rate": 0.05
    }
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### GET /metrics

Get aggregated metrics across regions.

**Query Parameters:**
- `regions` (optional): Comma-separated list of regions
- `metric_name` (required): Metric to retrieve
- `time_range` (optional): Time range in hours (default: 1)

**Response:**
```json
{
  "metric_name": "request_latency_p95",
  "by_region": {
    "us-east-1": 45.5,
    "eu-west-1": 52.3,
    "ap-southeast-1": 67.8
  },
  "global_average": 55.2,
  "timestamp": "2024-01-15T10:00:00Z"
}
```

**TODO for students**: Implement Prometheus-compatible metrics endpoint.

## Deployment APIs

### POST /deployments

Create a new multi-region deployment.

**Request:**
```json
{
  "version": "v2.0.0",
  "strategy": "rolling",
  "regions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
  "rollback_on_failure": true,
  "validation_period_seconds": 300
}
```

**Response:**
```json
{
  "deployment_id": "deploy-12345",
  "status": "in_progress",
  "started_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T10:30:00Z"
}
```

### GET /deployments/{deployment_id}

Get deployment status.

**Response:**
```json
{
  "deployment_id": "deploy-12345",
  "status": "completed",
  "strategy": "rolling",
  "deployed_regions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
  "failed_regions": [],
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:25:00Z"
}
```

**TODO for students**: Add endpoints for blue-green and canary deployments.

## Failover APIs

### POST /failover

Trigger manual failover between regions.

**Request:**
```json
{
  "from_region": "us-east-1",
  "to_region": "eu-west-1",
  "reason": "planned_maintenance",
  "drain_timeout_seconds": 300
}
```

**Response:**
```json
{
  "failover_id": "failover-12345",
  "status": "in_progress",
  "from_region": "us-east-1",
  "to_region": "eu-west-1",
  "initiated_at": "2024-01-15T10:00:00Z"
}
```

### POST /failover/{failover_id}/rollback

Rollback a failover operation.

**Response:**
```json
{
  "failover_id": "failover-12345",
  "status": "rolled_back",
  "completed_at": "2024-01-15T10:30:00Z"
}
```

## Cost APIs

### GET /cost/summary

Get cost summary across regions.

**Query Parameters:**
- `days` (optional): Number of days to include (default: 30)
- `regions` (optional): Filter by regions

**Response:**
```json
{
  "total_cost": 5000.50,
  "by_region": {
    "us-east-1": 2000.25,
    "eu-west-1": 1500.15,
    "ap-southeast-1": 1500.10
  },
  "by_resource_type": {
    "compute": 3000.00,
    "storage": 1000.00,
    "network": 500.50,
    "database": 500.00
  },
  "period_start": "2023-12-16T00:00:00Z",
  "period_end": "2024-01-15T23:59:59Z"
}
```

### GET /cost/recommendations

Get cost optimization recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "type": "right_sizing",
      "region": "ap-southeast-1",
      "resource_id": "i-1234567890abcdef0",
      "current_cost_monthly": 200.00,
      "projected_cost_monthly": 150.00,
      "savings_monthly": 50.00,
      "description": "Instance is over-provisioned based on CPU usage",
      "action": "Downsize from m5.xlarge to m5.large"
    }
  ],
  "total_potential_savings": 450.00
}
```

## Error Responses

All API errors follow this format:

```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model 'model-v1.0.0' not found in region us-east-1",
    "details": {
      "model_id": "model-v1.0.0",
      "region": "us-east-1"
    },
    "timestamp": "2024-01-15T10:00:00Z",
    "request_id": "req-12345"
  }
}
```

### Common Error Codes

- `400` - Bad Request: Invalid request parameters
- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server-side error
- `503` - Service Unavailable: Service temporarily unavailable

**TODO for students**: Define application-specific error codes and handling strategies.

## Rate Limiting

API requests are rate-limited per authentication token:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1642248000
```

**TODO for students**: Implement rate limiting using:
- Token bucket algorithm
- Redis for distributed rate limiting
- Different limits per endpoint and tier

## Versioning

The API uses URL-based versioning:

- `v1`: Current stable version
- `v2-beta`: Next version in development

**TODO for students**: Implement API versioning strategy and deprecation policy.

## WebSocket APIs

For real-time updates, connect to the WebSocket endpoint:

```
wss://ml-platform.example.com/api/v1/ws
```

**TODO for students**: Implement WebSocket support for:
- Real-time metrics streaming
- Deployment progress updates
- Alert notifications

## SDK Examples

### Python

```python
from ml_platform_client import MultiRegionClient

client = MultiRegionClient(
    api_key="your-api-key",
    global_endpoint="https://ml-platform.example.com"
)

# Make prediction
result = client.predict(
    model_id="model-v1.0.0",
    inputs=[[1.0, 2.0, 3.0, 4.0]]
)
print(result.predictions)
```

### cURL

```bash
curl -X POST "https://ml-platform.example.com/api/v1/models/model-v1.0.0/predict" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [[1.0, 2.0, 3.0, 4.0]],
    "parameters": {"batch_size": 1}
  }'
```

**TODO for students**: Create SDKs for Python, Go, and Node.js.

## API Testing

Use the provided Postman collection for testing:

```bash
# Import collection
postman import collection.json

# Run tests
newman run collection.json --environment production.json
```

**TODO for students**: Add comprehensive API tests and integration tests.
