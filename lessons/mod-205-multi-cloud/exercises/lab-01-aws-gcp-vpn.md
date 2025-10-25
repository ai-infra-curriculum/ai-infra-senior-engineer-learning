# Lab 1: AWS-GCP VPN Connection

## Objective

Set up a secure VPN connection between AWS and GCP to enable private communication between resources in both clouds.

## Prerequisites

- AWS account with appropriate permissions
- GCP project with appropriate permissions
- Terraform installed (version 1.0+)
- AWS CLI configured
- gcloud CLI configured
- Understanding of VPN and networking concepts

## Estimated Time

2-3 hours

---

## Architecture Overview

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│           AWS               │         │           GCP               │
│      (us-east-1)            │         │     (us-central1)           │
│                             │         │                             │
│  VPC: 10.0.0.0/16           │         │  VPC: 10.1.0.0/16           │
│  ┌───────────────────────┐  │         │  ┌───────────────────────┐  │
│  │  Private Subnet       │  │         │  │  Private Subnet       │  │
│  │  10.0.1.0/24          │  │         │  │  10.1.1.0/24          │  │
│  │                       │  │         │  │                       │  │
│  │  ┌──────────────┐     │  │         │  │  ┌──────────────┐     │  │
│  │  │ EC2 Instance │     │  │         │  │  │ GCE Instance │     │  │
│  │  │ 10.0.1.10    │     │  │         │  │  │ 10.1.1.10    │     │  │
│  │  └──────────────┘     │  │         │  │  └──────────────┘     │  │
│  └───────────────────────┘  │         │  └───────────────────────┘  │
│           ▲                 │         │           ▲                 │
│           │                 │         │           │                 │
│  ┌────────┴───────────────┐ │         │  ┌────────┴───────────────┐ │
│  │  Virtual Private       │ │         │  │  Cloud VPN Gateway     │ │
│  │  Gateway (VGW)         │ │         │  │                        │ │
│  │  AWS VPN Endpoint      │ │◄───────►│  │  GCP VPN Endpoint      │ │
│  └────────────────────────┘ │  IPsec  │  └────────────────────────┘ │
│                             │  Tunnel │                             │
└─────────────────────────────┘         └─────────────────────────────┘
```

---

## Part 1: AWS Setup

### Step 1.1: Create VPC and Subnets

Create a file `aws-vpc.tf`:

```hcl
# AWS Provider Configuration
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "multi-cloud-vpn-vpc"
    Environment = "lab"
    Project     = "multi-cloud-networking"
  }
}

# Private Subnet
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "private-subnet"
  }
}

# Internet Gateway (for NAT)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# Public Subnet for NAT Gateway
resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "public-subnet"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "nat-eip"
  }
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "main-nat"
  }
}

# Route Table for Public Subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Route Table for Private Subnet
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  # Route to GCP will be added after VPN is created
  route {
    cidr_block = "10.1.0.0/16"
    gateway_id = aws_vpn_gateway.main.id
  }

  tags = {
    Name = "private-rt"
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Output VPC ID
output "aws_vpc_id" {
  value = aws_vpc.main.id
}

output "aws_private_subnet_id" {
  value = aws_subnet.private.id
}
```

### Step 1.2: Create Virtual Private Gateway

Create `aws-vpn-gateway.tf`:

```hcl
# Virtual Private Gateway
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "gcp-vpn-gateway"
  }
}

# Customer Gateway (represents GCP VPN endpoint)
resource "aws_customer_gateway" "gcp" {
  bgp_asn    = 65000
  ip_address = google_compute_address.vpn_static_ip.address
  type       = "ipsec.1"

  tags = {
    Name = "gcp-customer-gateway"
  }
}

# VPN Connection
resource "aws_vpn_connection" "gcp" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.gcp.id
  type                = "ipsec.1"
  static_routes_only  = true

  tags = {
    Name = "aws-gcp-vpn"
  }
}

# Static Route to GCP
resource "aws_vpn_connection_route" "gcp" {
  destination_cidr_block = "10.1.0.0/16"
  vpn_connection_id      = aws_vpn_connection.gcp.id
}

# Outputs for GCP configuration
output "aws_vpn_tunnel1_address" {
  value = aws_vpn_connection.gcp.tunnel1_address
}

output "aws_vpn_tunnel1_preshared_key" {
  value     = aws_vpn_connection.gcp.tunnel1_preshared_key
  sensitive = true
}

output "aws_vpn_tunnel2_address" {
  value = aws_vpn_connection.gcp.tunnel2_address
}

output "aws_vpn_tunnel2_preshared_key" {
  value     = aws_vpn_connection.gcp.tunnel2_preshared_key
  sensitive = true
}
```

### Step 1.3: Create Test EC2 Instance

Create `aws-instance.tf`:

```hcl
# Security Group for Test Instance
resource "aws_security_group" "test_instance" {
  name        = "test-instance-sg"
  description = "Security group for test instance"
  vpc_id      = aws_vpc.main.id

  # Allow SSH from anywhere (for lab purposes only!)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow ICMP from GCP VPC
  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["10.1.0.0/16"]
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "test-instance-sg"
  }
}

# EC2 Instance
resource "aws_instance" "test" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 (update for your region)
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.private.id

  vpc_security_group_ids = [aws_security_group.test_instance.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y tcpdump telnet nc
              echo "AWS Test Instance" > /etc/motd
              EOF

  tags = {
    Name = "aws-test-instance"
  }
}

output "aws_instance_private_ip" {
  value = aws_instance.test.private_ip
}
```

---

## Part 2: GCP Setup

### Step 2.1: Create VPC and Subnets

Create `gcp-vpc.tf`:

```hcl
# GCP Provider Configuration
provider "google" {
  project = "YOUR_PROJECT_ID"
  region  = "us-central1"
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "multi-cloud-vpn-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "private" {
  name          = "private-subnet"
  ip_cidr_range = "10.1.1.0/24"
  region        = "us-central1"
  network       = google_compute_network.main.id

  private_ip_google_access = true
}

# Firewall rule to allow SSH
resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh"]
}

# Firewall rule to allow ICMP from AWS
resource "google_compute_firewall" "allow_icmp_from_aws" {
  name    = "allow-icmp-from-aws"
  network = google_compute_network.main.name

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/16"]
}

# Firewall rule to allow all internal traffic
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.1.0.0/16"]
}

output "gcp_vpc_name" {
  value = google_compute_network.main.name
}

output "gcp_subnet_name" {
  value = google_compute_subnetwork.private.name
}
```

### Step 2.2: Create Cloud VPN Gateway

Create `gcp-vpn.tf`:

```hcl
# Reserve Static IP for VPN Gateway
resource "google_compute_address" "vpn_static_ip" {
  name   = "vpn-static-ip"
  region = "us-central1"
}

# VPN Gateway
resource "google_compute_vpn_gateway" "target_gateway" {
  name    = "aws-vpn-gateway"
  network = google_compute_network.main.id
  region  = "us-central1"
}

# Forwarding rules for ESP protocol
resource "google_compute_forwarding_rule" "fr_esp" {
  name        = "fr-esp"
  ip_protocol = "ESP"
  ip_address  = google_compute_address.vpn_static_ip.address
  target      = google_compute_vpn_gateway.target_gateway.id
  region      = "us-central1"
}

# Forwarding rules for UDP 500 (IKE)
resource "google_compute_forwarding_rule" "fr_udp500" {
  name        = "fr-udp500"
  ip_protocol = "UDP"
  port_range  = "500"
  ip_address  = google_compute_address.vpn_static_ip.address
  target      = google_compute_vpn_gateway.target_gateway.id
  region      = "us-central1"
}

# Forwarding rules for UDP 4500 (NAT-T)
resource "google_compute_forwarding_rule" "fr_udp4500" {
  name        = "fr-udp4500"
  ip_protocol = "UDP"
  port_range  = "4500"
  ip_address  = google_compute_address.vpn_static_ip.address
  target      = google_compute_vpn_gateway.target_gateway.id
  region      = "us-central1"
}

# VPN Tunnel 1
resource "google_compute_vpn_tunnel" "tunnel1" {
  name          = "aws-tunnel1"
  peer_ip       = aws_vpn_connection.gcp.tunnel1_address
  shared_secret = aws_vpn_connection.gcp.tunnel1_preshared_key

  target_vpn_gateway = google_compute_vpn_gateway.target_gateway.id

  local_traffic_selector  = ["0.0.0.0/0"]
  remote_traffic_selector = ["0.0.0.0/0"]

  region = "us-central1"

  depends_on = [
    google_compute_forwarding_rule.fr_esp,
    google_compute_forwarding_rule.fr_udp500,
    google_compute_forwarding_rule.fr_udp4500,
  ]
}

# VPN Tunnel 2 (for redundancy)
resource "google_compute_vpn_tunnel" "tunnel2" {
  name          = "aws-tunnel2"
  peer_ip       = aws_vpn_connection.gcp.tunnel2_address
  shared_secret = aws_vpn_connection.gcp.tunnel2_preshared_key

  target_vpn_gateway = google_compute_vpn_gateway.target_gateway.id

  local_traffic_selector  = ["0.0.0.0/0"]
  remote_traffic_selector = ["0.0.0.0/0"]

  region = "us-central1"

  depends_on = [
    google_compute_forwarding_rule.fr_esp,
    google_compute_forwarding_rule.fr_udp500,
    google_compute_forwarding_rule.fr_udp4500,
  ]
}

# Route to AWS via Tunnel 1
resource "google_compute_route" "route_to_aws_tunnel1" {
  name       = "route-to-aws-tunnel1"
  network    = google_compute_network.main.name
  dest_range = "10.0.0.0/16"
  priority   = 1000

  next_hop_vpn_tunnel = google_compute_vpn_tunnel.tunnel1.id
}

# Route to AWS via Tunnel 2 (backup)
resource "google_compute_route" "route_to_aws_tunnel2" {
  name       = "route-to-aws-tunnel2"
  network    = google_compute_network.main.name
  dest_range = "10.0.0.0/16"
  priority   = 1001

  next_hop_vpn_tunnel = google_compute_vpn_tunnel.tunnel2.id
}

output "gcp_vpn_gateway_ip" {
  value = google_compute_address.vpn_static_ip.address
}
```

### Step 2.3: Create Test GCE Instance

Create `gcp-instance.tf`:

```hcl
# GCE Instance
resource "google_compute_instance" "test" {
  name         = "gcp-test-instance"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.private.name

    # Assign external IP for SSH access
    access_config {
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y tcpdump telnet netcat-openbsd
    echo "GCP Test Instance" > /etc/motd
  EOF

  tags = ["ssh"]
}

output "gcp_instance_private_ip" {
  value = google_compute_instance.test.network_interface[0].network_ip
}

output "gcp_instance_public_ip" {
  value = google_compute_instance.test.network_interface[0].access_config[0].nat_ip
}
```

---

## Part 3: Deploy Infrastructure

### Step 3.1: Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### Step 3.2: Verify VPN Connection

```bash
# Check AWS VPN Connection Status
aws ec2 describe-vpn-connections \
  --vpn-connection-ids $(terraform output -raw aws_vpn_connection_id) \
  --query 'VpnConnections[0].VgwTelemetry'

# Check GCP VPN Tunnel Status
gcloud compute vpn-tunnels describe aws-tunnel1 \
  --region us-central1 \
  --format="get(status)"

gcloud compute vpn-tunnels describe aws-tunnel2 \
  --region us-central1 \
  --format="get(status)"
```

Expected output: Both tunnels should show "UP" or "ESTABLISHED"

---

## Part 4: Test Connectivity

### Step 4.1: Test Ping from AWS to GCP

```bash
# Get instance IPs
AWS_INSTANCE_IP=$(terraform output -raw aws_instance_private_ip)
GCP_INSTANCE_IP=$(terraform output -raw gcp_instance_private_ip)

# SSH to AWS instance (via Session Manager or bastion)
aws ssm start-session --target $(terraform output -raw aws_instance_id)

# From AWS instance, ping GCP instance
ping $GCP_INSTANCE_IP
```

Expected output:
```
PING 10.1.1.10 (10.1.1.10) 56(84) bytes of data.
64 bytes from 10.1.1.10: icmp_seq=1 ttl=64 time=15.2 ms
64 bytes from 10.1.1.10: icmp_seq=2 ttl=64 time=14.8 ms
```

### Step 4.2: Test Ping from GCP to AWS

```bash
# SSH to GCP instance
gcloud compute ssh gcp-test-instance --zone us-central1-a

# From GCP instance, ping AWS instance
ping $AWS_INSTANCE_IP
```

### Step 4.3: Test TCP Connectivity

On GCP instance:
```bash
# Start a simple HTTP server
python3 -m http.server 8080
```

On AWS instance:
```bash
# Connect to GCP HTTP server
curl http://$GCP_INSTANCE_IP:8080
```

### Step 4.4: Monitor VPN Traffic

```bash
# On AWS side
aws cloudwatch get-metric-statistics \
  --namespace AWS/VPN \
  --metric-name TunnelDataIn \
  --dimensions Name=VpnId,Value=$(terraform output -raw aws_vpn_connection_id) \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# On GCP side
gcloud monitoring time-series list \
  --filter='metric.type="vpn.googleapis.com/network/received_bytes_count"' \
  --format=json
```

---

## Part 5: Performance Testing

### Step 5.1: Latency Test

```bash
# From AWS instance to GCP instance
ping -c 100 $GCP_INSTANCE_IP | tail -1

# Example output:
# rtt min/avg/max/mdev = 14.234/15.678/18.234/1.234 ms
```

### Step 5.2: Bandwidth Test

```bash
# Install iperf3 on both instances
# AWS:
sudo yum install -y iperf3

# GCP:
sudo apt-get install -y iperf3

# On GCP instance, start iperf3 server
iperf3 -s

# On AWS instance, run bandwidth test
iperf3 -c $GCP_INSTANCE_IP -t 30

# Expected output:
# [ ID] Interval           Transfer     Bitrate
# [  5]   0.00-30.00  sec  1.50 GBytes   429 Mbits/sec
```

### Step 5.3: Packet Loss Test

```bash
# Send 1000 pings and calculate packet loss
ping -c 1000 $GCP_INSTANCE_IP | grep "packet loss"

# Expected: 0% packet loss
```

---

## Part 6: Troubleshooting

### Common Issues

#### Issue 1: VPN Tunnel Down

**Symptoms:** Tunnel status shows "DOWN"

**Troubleshooting:**
```bash
# Check IKE logs on AWS
aws logs tail /aws/vpn/$(terraform output -raw aws_vpn_connection_id)

# Check GCP VPN tunnel details
gcloud compute vpn-tunnels describe aws-tunnel1 \
  --region us-central1 \
  --format=yaml

# Verify pre-shared keys match
terraform output aws_vpn_tunnel1_preshared_key
```

**Solutions:**
- Verify pre-shared keys match
- Check security group rules
- Verify routing configuration
- Confirm IP addresses are correct

#### Issue 2: Ping Not Working

**Symptoms:** VPN tunnel UP but ping fails

**Troubleshooting:**
```bash
# Check security groups/firewall rules
# AWS:
aws ec2 describe-security-groups --group-ids $(terraform output -raw aws_security_group_id)

# GCP:
gcloud compute firewall-rules list --filter="network:multi-cloud-vpn-vpc"

# Check routing tables
# AWS:
aws ec2 describe-route-tables --route-table-ids $(terraform output -raw aws_route_table_id)

# GCP:
gcloud compute routes list --filter="network:multi-cloud-vpn-vpc"

# Test with tcpdump
sudo tcpdump -i any -n icmp
```

**Solutions:**
- Add ICMP rules to security groups/firewall
- Verify route table entries
- Check source/destination checking on instances

#### Issue 3: High Latency

**Symptoms:** Latency > 50ms

**Troubleshooting:**
```bash
# Traceroute to identify where latency occurs
traceroute $GCP_INSTANCE_IP

# Check VPN tunnel metrics
# Monitor packet loss, jitter
```

**Solutions:**
- Choose closer regions
- Use dedicated interconnect for better performance
- Optimize MTU size

---

## Part 7: Cleanup

```bash
# Destroy all resources
terraform destroy

# Verify all resources are deleted
aws ec2 describe-vpn-connections
gcloud compute vpn-tunnels list
```

---

## Challenge Exercises

1. **High Availability:** Set up active-active VPN tunnels with equal cost multi-path routing

2. **BGP Dynamic Routing:** Configure BGP instead of static routes for automatic failover

3. **Multi-Region:** Extend the setup to include multiple AWS regions connecting to GCP

4. **Monitoring Dashboard:** Create a Grafana dashboard showing VPN metrics from both clouds

5. **Automated Failover:** Implement automated failover when primary tunnel goes down

---

## Learning Outcomes

After completing this lab, you should be able to:
- ✓ Configure VPN connections between AWS and GCP
- ✓ Set up routing for cross-cloud communication
- ✓ Troubleshoot VPN connectivity issues
- ✓ Monitor VPN performance and health
- ✓ Understand IPsec VPN fundamentals
- ✓ Implement secure multi-cloud networking

---

## Additional Resources

- [AWS VPN Documentation](https://docs.aws.amazon.com/vpn/)
- [GCP Cloud VPN Documentation](https://cloud.google.com/network-connectivity/docs/vpn)
- [IPsec VPN Best Practices](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNConnections.html)
- [Terraform AWS VPN Module](https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/)
- [Terraform GCP VPN Module](https://registry.terraform.io/modules/terraform-google-modules/vpn/google/)
