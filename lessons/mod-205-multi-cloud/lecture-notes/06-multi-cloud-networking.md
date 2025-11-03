# Multi-Cloud Networking Architecture

## Learning Objectives

By the end of this lecture, you will be able to:

- Design multi-cloud network topologies that connect AWS, GCP, and Azure workloads using VPN, dedicated interconnects, and transit gateway architectures
- Implement secure cross-cloud connectivity using AWS Direct Connect, Google Cloud Interconnect, and Azure ExpressRoute with BGP routing and private peering
- Architect network cost optimization strategies minimizing egress charges ($0.08-0.12/GB) through regional placement, CDN usage, and private connectivity options
- Configure multi-cloud VPN solutions using site-to-site VPNs, cloud VPN gateways, and high-availability IPsec tunnels for redundant connectivity
- Design IP address management (IPAM) strategies avoiding CIDR conflicts, implementing subnet planning, and managing address space across multiple clouds
- Implement network security controls including cloud-agnostic firewalls, network segmentation, DDoS protection, and Web Application Firewalls (WAF)
- Optimize network performance for ML workloads using placement groups, accelerated networking, jumbo frames, and bandwidth reservations for large data transfers
- Monitor multi-cloud network health with unified observability using VPC Flow Logs, network packet capture, latency monitoring, and cross-cloud trace analysis

## Overview

Networking is one of the most complex aspects of multi-cloud infrastructure. This lesson covers strategies for connecting workloads across AWS, GCP, and Azure, implementing secure connectivity, and optimizing network performance for AI workloads.

---

## 1. Multi-Cloud Networking Challenges

### Key Challenges

```
┌──────────────────────────────────────────────────────────┐
│              Multi-Cloud Networking Issues                │
├──────────────────────────────────────────────────────────┤
│ • Egress costs ($0.08-$0.12 per GB)                      │
│ • Latency between clouds (50-200ms)                      │
│ • Different networking models and APIs                    │
│ • Complex routing and firewall rules                     │
│ • Security and compliance requirements                   │
│ • IP address management across clouds                    │
│ • Inconsistent network performance                       │
└──────────────────────────────────────────────────────────┘
```

### Cost Implications

| Scenario | Cost/GB | Monthly Cost (1TB) |
|----------|---------|-------------------|
| Intra-region (same cloud) | $0.01 | $10 |
| Inter-region (same cloud) | $0.02 | $20 |
| Cloud to cloud (internet) | $0.09 | $90 |
| Cloud to cloud (private) | $0.05 | $50 |
| On-prem to cloud | $0.05-0.10 | $50-100 |

---

## 2. Cloud Interconnect Services

### AWS Direct Connect

**Architecture**

```
┌──────────────────┐
│   On-Premises    │
│   Data Center    │
└────────┬─────────┘
         │
    Direct Connect
    (1/10/100 Gbps)
         │
┌────────▼─────────┐
│   AWS Region     │
│  ┌────────────┐  │
│  │    VPC     │  │
│  └────────────┘  │
└──────────────────┘
```

**Configuration**

```terraform
# AWS Direct Connect Virtual Interface
resource "aws_dx_connection" "main" {
  name      = "ml-dx-connection"
  bandwidth = "10Gbps"
  location  = "EqDC2"  # Equinix DC2
}

resource "aws_dx_private_virtual_interface" "ml_vif" {
  connection_id = aws_dx_connection.main.id
  name          = "ml-private-vif"
  vlan          = 1000
  address_family = "ipv4"
  bgp_asn       = 65000

  # Connect to Virtual Private Gateway
  vpn_gateway_id = aws_vpn_gateway.main.id

  customer_address  = "169.254.0.1/30"
  amazon_address    = "169.254.0.2/30"
}

# Transit Gateway for multi-VPC connectivity
resource "aws_ec2_transit_gateway" "main" {
  description                     = "Multi-region transit gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                     = "enable"
  vpn_ecmp_support               = "enable"
}
```

### GCP Cloud Interconnect

**Partner Interconnect**

```terraform
resource "google_compute_interconnect_attachment" "ml_attachment" {
  name                     = "ml-interconnect"
  type                     = "PARTNER"
  router                   = google_compute_router.main.id
  region                   = "us-west1"
  admin_enabled            = true
  bandwidth                = "BPS_10G"
  edge_availability_domain = "AVAILABILITY_DOMAIN_1"
}

resource "google_compute_router" "main" {
  name    = "ml-cloud-router"
  region  = "us-west1"
  network = google_compute_network.main.id

  bgp {
    asn               = 64512
    advertise_mode    = "CUSTOM"
    advertised_groups = ["ALL_SUBNETS"]

    advertised_ip_ranges {
      range = "10.0.0.0/8"
    }
  }
}
```

### Azure ExpressRoute

**Configuration**

```terraform
resource "azurerm_express_route_circuit" "main" {
  name                  = "ml-expressroute"
  resource_group_name   = azurerm_resource_group.main.name
  location              = "West US 2"
  service_provider_name = "Equinix"
  peering_location      = "Silicon Valley"
  bandwidth_in_mbps     = 10000

  sku {
    tier   = "Premium"
    family = "MeteredData"
  }
}

resource "azurerm_express_route_circuit_peering" "private" {
  peering_type                  = "AzurePrivatePeering"
  express_route_circuit_name    = azurerm_express_route_circuit.main.name
  resource_group_name           = azurerm_resource_group.main.name
  peer_asn                      = 65000
  primary_peer_address_prefix   = "169.254.0.0/30"
  secondary_peer_address_prefix = "169.254.0.4/30"
  vlan_id                       = 100
}
```

---

## 3. Cloud-to-Cloud Connectivity

### Hub-and-Spoke Architecture

```
              ┌──────────────┐
              │  AWS Region  │
              │  (Hub VPC)   │
              │              │
              │  ┌────────┐  │
              │  │Transit │  │
              │  │Gateway │  │
              └──┴────┬───┴──┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼─────┐ ┌─────▼────┐ ┌─────▼────┐
│ GCP Region  │ │  Azure   │ │  AWS     │
│ (Spoke)     │ │ (Spoke)  │ │  Region2 │
│             │ │          │ │ (Spoke)  │
└─────────────┘ └──────────┘ └──────────┘
```

### VPN Mesh Between Clouds

**AWS Site-to-Site VPN**

```python
import boto3

ec2 = boto3.client('ec2', region_name='us-west-2')

# Create Customer Gateway (pointing to GCP)
customer_gateway = ec2.create_customer_gateway(
    Type='ipsec.1',
    BgpAsn=64512,  # GCP ASN
    PublicIp='35.123.45.67',  # GCP VPN gateway IP
    TagSpecifications=[
        {
            'ResourceType': 'customer-gateway',
            'Tags': [{'Key': 'Name', 'Value': 'gcp-gateway'}]
        }
    ]
)

# Create VPN Connection
vpn_connection = ec2.create_vpn_connection(
    Type='ipsec.1',
    CustomerGatewayId=customer_gateway['CustomerGateway']['CustomerGatewayId'],
    VpnGatewayId='vgw-xxxxx',
    Options={
        'StaticRoutesOnly': False,
        'TunnelOptions': [
            {
                'TunnelInsideCidr': '169.254.100.0/30',
                'PreSharedKey': 'my-secret-key'
            },
            {
                'TunnelInsideCidr': '169.254.100.4/30',
                'PreSharedKey': 'my-secret-key-2'
            }
        ]
    }
)
```

**GCP VPN to AWS**

```python
from google.cloud import compute_v1

# Create Cloud VPN Gateway
vpn_gateway = compute_v1.VpnGateway()
vpn_gateway.name = "aws-vpn-gateway"
vpn_gateway.network = "projects/<project>/global/networks/default"

gateways_client = compute_v1.VpnGatewaysClient()
operation = gateways_client.insert(
    project="<project-id>",
    region="us-west1",
    vpn_gateway_resource=vpn_gateway
)

# Create VPN Tunnel to AWS
vpn_tunnel = compute_v1.VpnTunnel()
vpn_tunnel.name = "tunnel-to-aws"
vpn_tunnel.peer_ip = "54.123.45.67"  # AWS VPN endpoint
vpn_tunnel.shared_secret = "my-secret-key"
vpn_tunnel.target_vpn_gateway = vpn_gateway.self_link
vpn_tunnel.router = "projects/<project>/regions/us-west1/routers/cloud-router"

tunnels_client = compute_v1.VpnTunnelsClient()
operation = tunnels_client.insert(
    project="<project-id>",
    region="us-west1",
    vpn_tunnel_resource=vpn_tunnel
)
```

### Third-Party SD-WAN Solutions

**Aviatrix Multi-Cloud Network**

```python
# Aviatrix Controller API
import requests

aviatrix_api = "https://controller.example.com/v1/api"
session = requests.Session()

# Create AWS gateway
aws_gateway = {
    "action": "create_gateway",
    "cloud_type": 1,  # AWS
    "account_name": "aws-prod",
    "gw_name": "aws-uswest2-gw",
    "vpc_id": "vpc-xxxxx",
    "vpc_reg": "us-west-2",
    "gw_size": "c5n.4xlarge",  # High network performance
    "subnet": "subnet-xxxxx",
    "enable_nat": "no"
}

# Create GCP gateway
gcp_gateway = {
    "action": "create_gateway",
    "cloud_type": 4,  # GCP
    "account_name": "gcp-prod",
    "gw_name": "gcp-uswest1-gw",
    "vpc_id": "vpc-name",
    "vpc_reg": "us-west1",
    "gw_size": "n1-highcpu-8",
    "subnet": "subnet-name",
    "zone": "us-west1-a"
}

# Create encrypted tunnel between gateways
tunnel_config = {
    "action": "create_site2cloud_conn",
    "conn_name": "aws-to-gcp",
    "gw_name": "aws-uswest2-gw",
    "remote_gw_ip": "<gcp-gateway-public-ip>",
    "pre_shared_key": "strong-psk",
    "remote_subnet": "10.10.0.0/16"  # GCP VPC CIDR
}
```

---

## 4. Network Performance Optimization

### Latency Optimization Strategies

**1. Edge Caching and CDN**

```python
# CloudFlare for multi-cloud edge caching
cloudflare_config = {
    'zones': [
        {
            'name': 'ml-api.example.com',
            'origins': [
                {'name': 'aws-origin', 'address': 'api-aws.example.com', 'weight': 50},
                {'name': 'gcp-origin', 'address': 'api-gcp.example.com', 'weight': 30},
                {'name': 'azure-origin', 'address': 'api-azure.example.com', 'weight': 20}
            ],
            'load_balancing': {
                'method': 'geo_proximity',
                'fallback_pool': 'aws-origin'
            }
        }
    ],
    'cache_rules': {
        '/api/models/*': {
            'cache_ttl': 3600,
            'edge_cache_ttl': 7200
        }
    }
}
```

**2. Multi-Cloud DNS with GeoDNS**

```yaml
# Route 53 geolocation routing
Resources:
  MLAPIRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref HostedZone
      Name: api.ml-platform.com
      Type: A
      SetIdentifier: US-West
      GeoLocation:
        ContinentCode: NA
      TTL: 60
      ResourceRecords:
        - 54.123.45.67  # AWS endpoint

  MLAPIRecordEU:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref HostedZone
      Name: api.ml-platform.com
      Type: A
      SetIdentifier: EU-West
      GeoLocation:
        ContinentCode: EU
      TTL: 60
      ResourceRecords:
        - 35.123.45.67  # GCP endpoint
```

**3. Data Transfer Acceleration**

```python
# AWS S3 Transfer Acceleration
import boto3

s3_client = boto3.client(
    's3',
    config=boto3.session.Config(
        s3={'use_accelerate_endpoint': True}
    )
)

# Upload with acceleration
s3_client.upload_file(
    'large-dataset.tar.gz',
    'ml-training-data',
    'datasets/large-dataset.tar.gz'
)

# GCP Transfer Service for cross-cloud data migration
from google.cloud import storage_transfer

transfer_client = storage_transfer.StorageTransferServiceClient()

# Transfer from AWS S3 to GCP GCS
transfer_job = {
    "description": "AWS to GCP data transfer",
    "project_id": "my-project",
    "transfer_spec": {
        "aws_s3_data_source": {
            "bucket_name": "aws-ml-datasets",
            "aws_access_key": {
                "access_key_id": "AKIAXXXXX",
                "secret_access_key": "secret"
            }
        },
        "gcs_data_sink": {
            "bucket_name": "gcp-ml-datasets"
        },
        "transfer_options": {
            "overwrite_objects_already_existing_in_sink": False
        }
    },
    "schedule": {
        "schedule_start_date": {"year": 2024, "month": 1, "day": 1}
    }
}

response = transfer_client.create_transfer_job(transfer_job=transfer_job)
```

---

## 5. Security in Multi-Cloud Networks

### Zero Trust Network Architecture

```
┌─────────────────────────────────────────────────────┐
│           Identity Provider (Okta/Auth0)             │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ OIDC/SAML
                    │
        ┌───────────▼───────────┐
        │  Identity-Aware Proxy  │
        │      (IAP/BeyondCorp)  │
        └───────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼────┐ ┌────▼────┐ ┌───▼──────┐
│  AWS VPC   │ │  GCP    │ │  Azure   │
│  + VPN     │ │  VPC    │ │  VNet    │
└────────────┘ └─────────┘ └──────────┘
```

**GCP Identity-Aware Proxy**

```python
from google.cloud import iap_v1

# Configure IAP for multi-cloud access
iap_client = iap_v1.IdentityAwareProxyAdminServiceClient()

# Enable IAP on backend service
backend_service = "projects/123/iap_web/compute/services/backend-service"

iap_settings = {
    "oauth2_client_id": "client-id.apps.googleusercontent.com",
    "oauth2_client_secret": "client-secret",
    "access_settings": {
        "allowed_domains": ["example.com"],
        "cors_settings": {
            "allow_http_options": True
        }
    }
}

iap_client.update_iap_settings(
    name=backend_service,
    iap_settings=iap_settings
)
```

### Network Segmentation

```python
# Terraform configuration for network segmentation
network_segments = """
# AWS Network Segments
resource "aws_vpc" "ml_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Environment = "production"
    Segment = "ml-workloads"
  }
}

resource "aws_subnet" "ml_training" {
  vpc_id     = aws_vpc.ml_vpc.id
  cidr_block = "10.0.1.0/24"
  tags = { Tier = "training" }
}

resource "aws_subnet" "ml_inference" {
  vpc_id     = aws_vpc.ml_vpc.id
  cidr_block = "10.0.2.0/24"
  tags = { Tier = "inference" }
}

resource "aws_subnet" "ml_data" {
  vpc_id     = aws_vpc.ml_vpc.id
  cidr_block = "10.0.3.0/24"
  tags = { Tier = "data" }
}

# Security groups for micro-segmentation
resource "aws_security_group" "training_sg" {
  vpc_id = aws_vpc.ml_vpc.id

  # Only allow traffic from inference subnet
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.2.0/24"]
  }

  # Allow access to data subnet
  egress {
    from_port   = 5432  # PostgreSQL
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.3.0/24"]
  }
}
"""
```

---

## 6. Monitoring and Observability

### Multi-Cloud Network Monitoring

```python
from datadog import initialize, api
import json

# Initialize Datadog for multi-cloud monitoring
initialize(
    api_key='<api-key>',
    app_key='<app-key>'
)

# Create multi-cloud network monitor
monitor_options = {
    "name": "Multi-Cloud Network Latency",
    "type": "metric alert",
    "query": "avg(last_5m):avg:network.latency{cloud:aws,cloud:gcp,cloud:azure} > 100",
    "message": """
        Network latency across clouds exceeds threshold.
        AWS->GCP: {{aws_to_gcp_latency.last}}ms
        AWS->Azure: {{aws_to_azure_latency.last}}ms
        GCP->Azure: {{gcp_to_azure_latency.last}}ms
        @pagerduty-network-team
    """,
    "tags": ["multi-cloud", "network", "latency"],
    "options": {
        "notify_no_data": True,
        "no_data_timeframe": 10,
        "notify_audit": True,
        "thresholds": {
            "critical": 100,
            "warning": 75
        }
    }
}

api.Monitor.create(**monitor_options)
```

### Network Flow Analysis

```python
# Elastic APM for distributed tracing across clouds
from elasticapm import Client

apm_client = Client(
    {
        'SERVICE_NAME': 'ml-inference-service',
        'SERVER_URL': 'https://apm.example.com',
        'ENVIRONMENT': 'production'
    }
)

# Trace cross-cloud API calls
@apm_client.capture_span()
def call_remote_service(cloud_provider, endpoint):
    """Track latency and errors for cross-cloud calls"""

    with apm_client.begin_transaction('cross-cloud-call'):
        apm_client.tag(cloud=cloud_provider, endpoint=endpoint)

        start_time = time.time()
        response = requests.post(endpoint, json=data)
        latency = (time.time() - start_time) * 1000

        apm_client.label(latency_ms=latency, status=response.status_code)

        return response
```

---

## 7. Best Practices

### Network Design DO's ✅

- Use private connectivity (VPN/Interconnect) for production workloads
- Implement network segmentation and micro-segmentation
- Enable VPC Flow Logs on all clouds for security analysis
- Use Content Delivery Networks (CDN) for global distribution
- Implement DNS-based load balancing for multi-cloud failover
- Monitor network performance continuously
- Use compression for data transfer between clouds
- Implement circuit breakers for cross-cloud calls

### Network Design DON'Ts ❌

- Don't rely on public internet for production workloads
- Don't use overly complex network topologies
- Don't forget to monitor egress costs
- Don't expose management interfaces publicly
- Don't use default security groups/firewall rules
- Don't ignore network latency in architecture decisions
- Don't transfer large datasets without cost analysis
- Don't skip disaster recovery testing

---

## Hands-On Exercise

Design and implement a multi-cloud network that:
1. Connects AWS, GCP, and Azure using VPN mesh
2. Implements geo-based DNS routing
3. Monitors cross-cloud network latency
4. Optimizes data transfer costs
5. Implements zero-trust security

---

## Key Takeaways

1. **Multi-cloud networking is complex** but essential for resilience
2. **Private connectivity** significantly reduces latency and improves security
3. **Egress costs** can be 10x higher than intra-cloud transfers
4. **Network segmentation** is critical for security and compliance
5. **Monitoring** is essential to optimize performance and costs
6. **SD-WAN solutions** can simplify multi-cloud connectivity
7. **Zero-trust architecture** should be the default approach

---

## Additional Resources

- [AWS Direct Connect Documentation](https://aws.amazon.com/directconnect/)
- [GCP Cloud Interconnect](https://cloud.google.com/network-connectivity/docs/interconnect)
- [Azure ExpressRoute](https://docs.microsoft.com/azure/expressroute/)
- [Aviatrix Multi-Cloud Network Architecture](https://aviatrix.com/learn-center/)
- [HashiCorp Consul for Multi-Cloud Service Mesh](https://www.consul.io/)
