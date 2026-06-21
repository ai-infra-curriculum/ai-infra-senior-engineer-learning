# Senior AI Infrastructure Engineer - Learning Repository

<!-- aicg:site-banner -->
> 🎓 Part of the **free, open-source AI Infrastructure Curriculum**. For live, instructor-led **[cohorts](https://ai-infra-curriculum.github.io/junior.html)** and **[team programs](https://ai-infra-curriculum.github.io/teams.html)**, visit **[ai-infra-curriculum.github.io](https://ai-infra-curriculum.github.io/)**.
<!-- /aicg:site-banner -->

![AI Infrastructure](https://img.shields.io/badge/AI-Infrastructure-blue)
![Level](https://img.shields.io/badge/Level-Senior%20Engineer-orange)
![Estimated Time](https://img.shields.io/badge/Time-400--500%20hours-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> A comprehensive, hands-on curriculum for advancing from AI Infrastructure Engineer to Senior AI Infrastructure Engineer level. Master distributed systems, advanced Kubernetes, multi-cloud architectures, and production ML infrastructure at scale.

## Table of Contents

- [Overview](#overview)
- [Learning Outcomes](#learning-outcomes)
- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [Curriculum Overview](#curriculum-overview)
- [Modules](#modules)
- [Projects](#projects)
- [Getting Started](#getting-started)
- [Study Path](#study-path)
- [Assessment and Certification](#assessment-and-certification)
- [Time Commitment](#time-commitment)
- [Technologies Covered](#technologies-covered)
- [Community and Support](#community-and-support)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

This repository contains the complete learning materials for the **Senior AI Infrastructure Engineer** level of the AI Infrastructure Career Path Curriculum. This is a production-oriented, hands-on curriculum designed to take experienced AI Infrastructure Engineers to the senior level through advanced concepts, real-world projects, and production-grade implementations.

### What Makes This Senior-Level?

At the senior engineer level, you will:
- **Design and implement** complex distributed ML systems across multiple clusters and clouds
- **Optimize performance** of GPU-intensive workloads and large-scale model training
- **Lead technical decisions** for ML infrastructure architecture and technology selection
- **Mentor junior engineers** and contribute to technical standards and best practices
- **Operate production systems** at enterprise scale with high availability and reliability requirements
- **Navigate multi-cloud** environments and implement cost-effective infrastructure strategies

### Target Role Description

**Senior AI Infrastructure Engineers** are responsible for:
- Designing and building distributed training platforms for large models
- Implementing high-performance model serving systems with advanced optimization (TensorRT, ONNX, vLLM)
- Managing multi-region, multi-cloud ML infrastructure
- Building custom Kubernetes operators for ML-specific workloads
- Establishing MLOps best practices and CI/CD pipelines for ML systems
- Implementing comprehensive observability and SRE practices for ML platforms
- Mentoring team members and conducting technical reviews
- Making strategic technology decisions for ML infrastructure

**Typical Seniority**: 4-7 years of experience in infrastructure/ML engineering

**Salary Range**: $140,000 - $220,000 USD (varies by location and company)

---

## Learning Outcomes

By completing this curriculum, you will be able to:

### Technical Skills

1. **Advanced Kubernetes & Cloud-Native**
   - Design and implement custom Kubernetes operators for ML workloads
   - Configure advanced scheduling strategies including GPU sharing and gang scheduling
   - Deploy and manage service meshes (Istio/Linkerd) for ML microservices
   - Implement multi-cluster architectures with federation and cross-cluster communication

2. **Distributed Training at Scale**
   - Build distributed training platforms using Ray, Horovod, and PyTorch DDP
   - Optimize NCCL communication for multi-node GPU training
   - Implement fault-tolerant checkpointing and automatic recovery
   - Design efficient data pipelines for distributed training

3. **GPU Computing & Optimization**
   - Optimize CUDA kernels and GPU memory management for ML workloads
   - Implement model optimization with TensorRT, ONNX Runtime, and quantization
   - Configure and tune multi-GPU and multi-node training jobs
   - Monitor and optimize GPU utilization across clusters

4. **Advanced Model Serving**
   - Deploy high-performance model servers with TensorRT and vLLM
   - Implement advanced batching, caching, and request routing strategies
   - Build autoscaling systems based on custom metrics and GPU utilization
   - Optimize inference latency and throughput for production workloads

5. **Multi-Cloud Architecture**
   - Design cloud-agnostic ML infrastructure using Terraform and Pulumi
   - Implement multi-region deployments with data replication and failover
   - Build cost optimization strategies across AWS, GCP, and Azure
   - Manage hybrid cloud and on-premises ML infrastructure

6. **Advanced MLOps**
   - Build end-to-end ML pipelines with Kubeflow, MLflow, and custom orchestration
   - Implement feature stores, model registries, and experiment tracking
   - Design CI/CD pipelines for ML model deployment
   - Establish model governance, versioning, and rollback strategies

7. **Observability & SRE**
   - Implement comprehensive observability with Prometheus, Grafana, and OpenTelemetry
   - Design SLIs, SLOs, and SLAs for ML systems
   - Build distributed tracing for ML inference pipelines
   - Implement incident response procedures and postmortem processes

8. **Infrastructure as Code & GitOps**
   - Manage infrastructure with Terraform, Pulumi, and Crossplane
   - Implement GitOps workflows with ArgoCD and Flux
   - Design declarative infrastructure patterns for ML platforms
   - Build self-service infrastructure portals

9. **Security & Compliance**
   - Implement zero-trust security for ML infrastructure
   - Design RBAC and access control for multi-tenant ML platforms
   - Ensure compliance with SOC2, HIPAA, and GDPR requirements
   - Implement secrets management and encryption strategies

10. **Technical Leadership**
    - Design technical architecture documents and RFCs
    - Conduct code reviews and establish engineering standards
    - Mentor junior engineers and lead technical discussions
    - Make build-vs-buy decisions and evaluate new technologies

### Career Skills

- Technical writing and documentation
- System design and architecture
- Performance benchmarking and optimization
- Incident management and on-call responsibilities
- Cross-functional collaboration with ML scientists and product teams
- Technical mentorship and knowledge sharing

---

## Prerequisites

### Required Completion

You should have completed the **AI Infrastructure Engineer** level curriculum or have equivalent experience:
- **Completed**: All modules 101-110 from the Engineer-level curriculum
- **Completed**: All projects 101-105 from the Engineer-level curriculum
- **Or**: 2-3 years of hands-on experience in ML infrastructure

### Required Knowledge

- **Programming**: Advanced Python (async, decorators, metaclasses), basic Go
- **Kubernetes**: Intermediate to advanced (operators, CRDs, networking, storage)
- **ML Frameworks**: Experience with PyTorch or TensorFlow training and inference
- **Cloud Platforms**: Working knowledge of at least one major cloud (AWS/GCP/Azure)
- **Infrastructure as Code**: Experience with Terraform or similar tools
- **Containerization**: Docker expertise including multi-stage builds and optimization
- **Monitoring**: Prometheus and Grafana fundamentals
- **Linux Systems**: Advanced command-line skills, systemd, networking

### Technical Prerequisites

- **Development Machine**: 16GB+ RAM, 4+ cores, 100GB+ available storage
- **Cloud Access**: AWS, GCP, or Azure account with ability to provision resources
- **GPU Access**: Access to GPU instances (can use cloud credits or local GPUs)
- **Kubernetes Cluster**: Ability to create clusters (Minikube, kind, or cloud-managed)
- **GitHub Account**: For accessing repositories and submitting work
- **Domain Knowledge**: Understanding of ML model training and inference workflows

### Recommended Background

- Bachelor's degree in Computer Science or related field (or equivalent experience)
- 3+ years of software engineering or infrastructure experience
- 1+ years working with ML/AI systems
- Production operations experience with on-call responsibilities

---

## Repository Structure

```
ai-infra-senior-engineer-learning/
├── README.md                          # This file - repository overview
├── CURRICULUM.md                      # Detailed curriculum guide with learning paths
├── CONTRIBUTING.md                    # Guidelines for contributing
├── LICENSE                            # MIT License
│
├── .github/                           # GitHub workflows and templates
│   ├── workflows/
│   │   ├── validate-code.yml         # Code validation CI
│   │   └── test-stubs.yml            # Test code stubs
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── lessons/                           # 10 comprehensive modules (mod-201 to mod-210)
│   ├── mod-201-advanced-kubernetes/   # Advanced K8s, operators, multi-cluster
│   ├── mod-202-distributed-training/  # Ray, Horovod, PyTorch DDP
│   ├── mod-203-gpu-computing/         # CUDA, GPU optimization, multi-GPU
│   ├── mod-204-model-optimization/    # TensorRT, ONNX, quantization
│   ├── mod-205-multi-cloud/           # Multi-cloud architecture, hybrid cloud
│   ├── mod-206-advanced-mlops/        # Kubeflow, feature stores, pipelines
│   ├── mod-207-observability-sre/     # Prometheus, SRE practices, SLOs
│   ├── mod-208-iac-gitops/            # Terraform, Pulumi, ArgoCD, Flux
│   ├── mod-209-security-compliance/   # Zero-trust, RBAC, compliance
│   └── mod-210-technical-leadership/  # Architecture, mentoring, RFCs
│
├── projects/                          # 4 hands-on capstone projects
│   ├── project-201-distributed-training/  # Ray-based distributed training platform
│   ├── project-202-model-serving/         # High-performance model serving with TensorRT
│   ├── project-203-multi-region/          # Multi-region ML platform
│   └── project-204-k8s-operator/          # Custom Kubernetes operator for ML jobs
│
├── assessments/                       # Quizzes and practical exams
│   ├── quizzes/                       # Module-specific quizzes
│   │   ├── quiz-201.md
│   │   ├── quiz-202.md
│   │   └── ...
│   └── practical-exams/               # Hands-on assessments
│       ├── midterm-exam.md
│       └── final-exam.md
│
└── resources/                         # Additional learning resources
    ├── reading-list.md                # Recommended books and papers
    ├── tools.md                       # Tool recommendations and guides
    ├── cheatsheets/                   # Quick reference guides
    └── references.md                  # Links to external resources
```

### Module Structure

Each module follows a consistent structure:

```
mod-XXX-topic-name/
├── README.md                  # Module overview, objectives, prerequisites
├── lecture-notes/             # Detailed lecture materials
│   ├── 01-topic-one.md
│   ├── 02-topic-two.md
│   └── ...
├── exercises/                 # Hands-on labs and exercises
│   ├── lab-01-*.md
│   ├── lab-02-*.md
│   └── quiz.md
└── resources/                 # Module-specific resources
    ├── recommended-reading.md
    └── tools-and-frameworks.md
```

### Project Structure

Each project includes:

```
project-XXX-name/
├── README.md                  # Project overview and quick start
├── requirements.md            # Detailed requirements
├── architecture.md            # Architecture documentation
├── src/                       # Code stubs with TODOs
│   └── (organized by component)
├── tests/                     # Test stubs
│   └── test_*.py
├── kubernetes/                # K8s manifests
├── docs/                      # Project documentation
│   ├── DESIGN.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── scripts/                   # Helper scripts
├── .env.example               # Environment template
└── requirements.txt           # Python dependencies
```

---

## Curriculum Overview

The curriculum is organized into **10 modules** and **4 major projects**, totaling approximately **400-500 hours** of learning content.

### Curriculum Philosophy

1. **Hands-On First**: Every concept is reinforced with practical exercises
2. **Production-Ready**: Focus on real-world, production-grade implementations
3. **Progressive Complexity**: Each module builds upon previous knowledge
4. **Project-Integrated**: Projects synthesize concepts from multiple modules
5. **Best Practices**: Emphasize industry standards and battle-tested patterns

### Learning Pathway

```
Modules 201-202 → Project 201 → Modules 203-204 → Project 202 →
Modules 205-207 → Project 203 → Modules 208-210 → Project 204
```

See [CURRICULUM.md](CURRICULUM.md) for detailed learning paths and schedules.

---

## Modules

### Module 201: Advanced Kubernetes and Cloud-Native Architecture (60 hours)
**Focus**: Custom operators, advanced scheduling, multi-cluster architecture

**Key Topics**:
- Kubernetes operators and Custom Resource Definitions (CRDs)
- Advanced scheduling: GPU sharing, gang scheduling, priority classes
- StatefulSets and storage architecture for ML workloads
- Service mesh deployment (Istio/Linkerd)
- Multi-cluster federation and cross-cluster communication
- Production Kubernetes: HA, DR, security, RBAC

**Learning Outcomes**: Design and operate production Kubernetes clusters for ML workloads

---

### Module 202: Distributed Training Systems (50 hours)
**Focus**: Ray, Horovod, PyTorch DDP for multi-node training

**Key Topics**:
- Distributed training architectures and patterns
- Ray Train for distributed PyTorch/TensorFlow
- NCCL optimization for GPU communication
- Fault tolerance and checkpointing
- Hyperparameter tuning with Ray Tune
- Profiling and optimizing distributed training

**Learning Outcomes**: Build and operate distributed training platforms at scale

---

### Module 203: GPU Computing and Optimization (45 hours)
**Focus**: CUDA fundamentals, multi-GPU systems, performance optimization

**Key Topics**:
- CUDA programming fundamentals
- GPU memory management and optimization
- Multi-GPU and multi-node training
- GPU monitoring and profiling (NVIDIA tools)
- NVIDIA container toolkit and GPU operators
- Cost optimization for GPU workloads

**Learning Outcomes**: Optimize GPU utilization and performance for ML workloads

---

### Module 204: Model Optimization and Acceleration (50 hours)
**Focus**: TensorRT, ONNX Runtime, quantization, distillation

**Key Topics**:
- Model optimization techniques (quantization, pruning, distillation)
- TensorRT for NVIDIA GPUs
- ONNX Runtime optimization
- Compiler-based optimization (TVM, XLA)
- Benchmark and profiling inference performance
- Hardware-specific optimizations (CPU, GPU, TPU)

**Learning Outcomes**: Deploy optimized, production-ready ML models with maximum performance

---

### Module 205: Multi-Cloud Architecture (40 hours)
**Focus**: Cloud-agnostic design, hybrid cloud, multi-region deployments

**Key Topics**:
- Multi-cloud architecture patterns
- Cloud-agnostic infrastructure with Terraform/Pulumi
- Multi-region deployment strategies
- Data replication and consistency
- Cost optimization across clouds
- Hybrid cloud and on-premises integration

**Learning Outcomes**: Design and implement multi-cloud ML infrastructure

---

### Module 206: Advanced MLOps and ML Pipelines (55 hours)
**Focus**: End-to-end ML pipelines, feature stores, model governance

**Key Topics**:
- Kubeflow Pipelines and custom orchestration
- Feature stores (Feast, Tecton)
- Model registries and versioning
- Experiment tracking at scale (MLflow, Weights & Biases)
- ML pipeline patterns and best practices
- Model governance and audit trails

**Learning Outcomes**: Build production ML pipelines with governance and reproducibility

---

### Module 207: Observability and SRE Practices (50 hours)
**Focus**: Prometheus, Grafana, OpenTelemetry, SRE for ML systems

**Key Topics**:
- Observability stack: Prometheus, Grafana, OpenTelemetry
- Distributed tracing for ML pipelines
- SLIs, SLOs, and SLAs for ML systems
- Alerting and incident response
- Capacity planning and resource management
- Error budgets and reliability engineering

**Learning Outcomes**: Implement comprehensive observability and SRE practices for ML platforms

---

### Module 208: Infrastructure as Code and GitOps (40 hours)
**Focus**: Terraform, Pulumi, ArgoCD, Flux

**Key Topics**:
- Advanced Terraform patterns and modules
- Pulumi for infrastructure as code
- GitOps principles and workflows
- ArgoCD and Flux for Kubernetes deployments
- Self-service infrastructure portals
- Infrastructure testing and validation

**Learning Outcomes**: Manage ML infrastructure declaratively with GitOps

---

### Module 209: Security and Compliance (35 hours)
**Focus**: Zero-trust security, compliance, secrets management

**Key Topics**:
- Zero-trust architecture for ML systems
- RBAC and access control for multi-tenant platforms
- Secrets management (Vault, external secret operators)
- Compliance frameworks (SOC2, HIPAA, GDPR)
- Container and image security
- Network security and policies

**Learning Outcomes**: Implement secure, compliant ML infrastructure

---

### Module 210: Technical Leadership and Communication (25 hours)
**Focus**: Architecture design, RFCs, mentoring, technical strategy

**Key Topics**:
- Writing technical architecture documents
- RFC processes and decision-making
- Code review best practices
- Technical mentoring and knowledge sharing
- Evaluating and adopting new technologies
- Build vs. buy decision frameworks
- Technical communication and stakeholder management

**Learning Outcomes**: Lead technical initiatives and mentor engineering teams

---

## Projects

### Project 201: Distributed Training Platform with Ray (60 hours)
**Complexity**: High | **Integration**: Modules 201, 202, 203

Build a production-ready distributed training platform using Ray Train that scales PyTorch models across multiple GPU nodes.

**What You'll Build**:
- Ray cluster on Kubernetes with GPU support
- Distributed training pipeline with PyTorch DDP
- Fault-tolerant checkpointing system
- Hyperparameter tuning with Ray Tune
- Monitoring with Prometheus and Grafana
- NCCL optimization for multi-node communication

**Technologies**: Ray, PyTorch, Kubernetes, NCCL, MLflow, Prometheus

**Success Criteria**:
- Train models across 4+ GPU nodes with >80% scaling efficiency
- Automatic recovery from node failures
- GPU utilization >85% during training

---

### Project 202: High-Performance Model Serving (70 hours)
**Complexity**: High | **Integration**: Modules 203, 204, 206

Build a high-performance model serving system with TensorRT optimization, advanced batching, and autoscaling.

**What You'll Build**:
- Multi-model serving platform with FastAPI/gRPC
- TensorRT optimization pipeline for NVIDIA GPUs
- Dynamic batching and request routing
- Autoscaling based on GPU metrics
- A/B testing and traffic splitting
- Distributed tracing with OpenTelemetry

**Technologies**: TensorRT, vLLM, Triton Inference Server, Kubernetes, Istio

**Success Criteria**:
- Inference latency <50ms for typical models
- GPU utilization >70% during serving
- Support 1000+ requests per second

---

### Project 203: Multi-Region ML Platform (70 hours)
**Complexity**: Very High | **Integration**: Modules 205, 207, 208

Design and implement a multi-region, multi-cloud ML platform with global load balancing and data replication.

**What You'll Build**:
- Multi-region Kubernetes clusters (3+ regions)
- Cloud-agnostic infrastructure with Terraform
- Global load balancing and traffic routing
- Cross-region data replication
- Disaster recovery and failover mechanisms
- Cost optimization dashboard

**Technologies**: Terraform, Kubernetes, Istio, Cloud providers (AWS/GCP/Azure)

**Success Criteria**:
- <100ms latency for nearest region
- Automatic failover in <30 seconds
- Cost reduced by 20%+ through optimization

---

### Project 204: Kubernetes Operator for ML Training Jobs (65 hours)
**Complexity**: Very High | **Integration**: Modules 201, 206, 209

Build a custom Kubernetes operator to manage ML training job lifecycle, resource allocation, and job scheduling.

**What You'll Build**:
- Custom Kubernetes operator in Go
- Custom Resource Definitions for ML jobs
- Job scheduling with GPU awareness
- Automatic resource cleanup
- Integration with MLflow and artifact storage
- RBAC and multi-tenancy support

**Technologies**: Go, Kubernetes, operator-sdk, MLflow

**Success Criteria**:
- Successfully manage 50+ concurrent training jobs
- Automatic GPU resource allocation
- Complete job lifecycle management (submit, monitor, cleanup)

---

## Getting Started

### 1. Assess Your Readiness

Before starting, complete the prerequisites self-assessment:

```bash
# Clone the repository
git clone https://github.com/ai-infra-curriculum/ai-infra-senior-engineer-learning.git
cd ai-infra-senior-engineer-learning

# Review prerequisites checklist
cat resources/prerequisites-checklist.md
```

### 2. Set Up Your Development Environment

```bash
# Install required tools
# - Python 3.11+
# - Docker Desktop or Podman
# - kubectl
# - Terraform
# - VS Code or preferred IDE

# Verify installations
python --version  # Should be 3.11+
docker --version
kubectl version --client
terraform --version
```

### 3. Choose Your Learning Path

See [CURRICULUM.md](CURRICULUM.md) for detailed paths:
- **Full-Time Track**: 3-4 months (40 hours/week)
- **Part-Time Track**: 6-8 months (15-20 hours/week)
- **Self-Paced Track**: Flexible timeline

### 4. Start with Module 201

```bash
cd lessons/mod-201-advanced-kubernetes
cat README.md  # Read module overview
```

### 5. Join the Community

- Slack: `#senior-engineer-learning`
- Discussion Forum: [GitHub Discussions](https://github.com/ai-infra-curriculum/ai-infra-senior-engineer-learning/discussions)
- Office Hours: Fridays 2-3pm PST

---

## Study Path

### Recommended Full-Time Study Plan (16 weeks)

**Weeks 1-3**: Modules 201-202 + Start Project 201
**Weeks 4-5**: Complete Project 201
**Weeks 6-8**: Modules 203-204 + Start Project 202
**Weeks 9-10**: Complete Project 202
**Weeks 11-13**: Modules 205-207 + Start Project 203
**Week 14**: Complete Project 203 + Modules 208-209
**Week 15**: Module 210 + Project 204
**Week 16**: Complete Project 204 + Final Assessment

### Recommended Part-Time Study Plan (32 weeks)

**Weeks 1-6**: Module 201-202 (10 hours/week)
**Weeks 7-10**: Project 201 (15 hours/week)
**Weeks 11-16**: Modules 203-204 (10 hours/week)
**Weeks 17-21**: Project 202 (15 hours/week)
**Weeks 22-27**: Modules 205-207 (10 hours/week)
**Weeks 28-32**: Project 203 + 204 + Modules 208-210 (15 hours/week)

---

## Assessment and Certification

### Module Assessments

Each module includes:
- **Quiz**: 20-25 questions testing conceptual understanding
- **Lab Completion**: Hands-on exercises verified through code submission
- **Passing Score**: 80% or higher

### Project Assessments

Projects are evaluated on:
- **Functionality**: Does it work as specified? (40%)
- **Code Quality**: Well-structured, tested, documented? (30%)
- **Performance**: Meets performance benchmarks? (20%)
- **Best Practices**: Follows industry standards? (10%)

### Final Certification

Requirements:
- Complete all 10 modules with passing scores
- Complete all 4 projects with >80% grade
- Pass final practical exam (8-hour capstone project)

**Certificate**: Senior AI Infrastructure Engineer Certification

---

## Time Commitment

### Total Estimated Hours: 400-500 hours

**Modules**: 450 hours
- Lecture materials: 180 hours
- Hands-on labs: 220 hours
- Quizzes and review: 50 hours

**Projects**: 265 hours
- Project 201: 60 hours
- Project 202: 70 hours
- Project 203: 70 hours
- Project 204: 65 hours

**Assessment**: 20 hours
- Module quizzes: 10 hours
- Final exam: 8 hours
- Review and preparation: 2 hours

### Weekly Time Commitment Options

- **Accelerated** (Full-time): 40 hours/week → 12-14 weeks
- **Standard** (Part-time): 20 hours/week → 24-28 weeks
- **Gradual** (Evening/weekend): 10 hours/week → 48-52 weeks

---

## Technologies Covered

### Core Technologies

**Container Orchestration**:
- Kubernetes (advanced features, operators, CRDs)
- Docker (multi-stage builds, optimization)
- Helm, Kustomize

**ML Frameworks**:
- PyTorch (distributed training, DDP)
- TensorFlow (distributed strategies)
- Ray (Train, Tune, Serve)
- Horovod

**Model Serving**:
- TensorRT, ONNX Runtime
- vLLM, Triton Inference Server
- FastAPI, gRPC

**Infrastructure as Code**:
- Terraform, Pulumi
- ArgoCD, Flux (GitOps)
- Crossplane

**Observability**:
- Prometheus, Grafana
- OpenTelemetry, Jaeger
- ELK Stack

**Cloud Platforms**:
- AWS (EKS, SageMaker, EC2)
- GCP (GKE, Vertex AI, Compute Engine)
- Azure (AKS, ML Studio)

**MLOps Tools**:
- Kubeflow Pipelines
- MLflow, Weights & Biases
- Feature stores (Feast, Tecton)

**GPU Technologies**:
- CUDA, cuDNN
- NCCL for multi-GPU communication
- NVIDIA container toolkit
- DCGM (GPU monitoring)

**Programming Languages**:
- Python (advanced)
- Go (for operators)
- Bash scripting

---

## Community and Support

### Discussion Forums

- **GitHub Discussions**: Technical questions and discussions
- **Slack Workspace**: Real-time chat and study groups
- **Stack Overflow**: Tag with `ai-infra-curriculum`

### Office Hours

- **Weekly Sessions**: Fridays 2-3pm PST
- **Format**: Q&A, code reviews, career advice
- **Recording**: Available on YouTube

### Study Groups

Form or join study groups:
- Regional meetups
- Virtual study sessions
- Project collaboration groups

### Mentorship

- **Peer Mentorship**: Connect with fellow learners
- **Industry Mentors**: Quarterly AMAs with senior engineers
- **Code Reviews**: Submit code for community review

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to contribute content improvements
- Code quality standards
- Pull request process
- Issue reporting guidelines

**Ways to Contribute**:
- Fix typos or improve documentation
- Add new exercises or examples
- Share your project implementations
- Suggest new topics or modules
- Create cheatsheets or reference materials

---

## License

This curriculum is released under the **MIT License**.

You are free to:
- Use the materials for learning
- Modify and adapt for your needs
- Share with others
- Use in corporate training (with attribution)

See [LICENSE](LICENSE) for full details.

---

## Contact

**AI Infrastructure Curriculum Team**

- **Email**: ai-infra-curriculum@joshua-ferguson.com
- **GitHub**: [@ai-infra-curriculum](https://github.com/ai-infra-curriculum)
- **Website**: [Coming Soon]
- **Twitter**: [@ai_infra_curr](https://twitter.com/ai_infra_curr)

---

## Acknowledgments

This curriculum was developed with input from:
- Senior ML infrastructure engineers at leading tech companies
- Open-source maintainers of key ML infrastructure tools
- Academic researchers in distributed systems and ML
- Early learners who provided feedback and testing

Special thanks to the communities behind Kubernetes, Ray, PyTorch, and TensorFlow.

---

## Frequently Asked Questions

**Q: Do I need to complete the Engineer-level curriculum first?**
A: Yes, or demonstrate equivalent experience through the prerequisites assessment.

**Q: Can I skip modules I'm already familiar with?**
A: You can test out of modules by passing the quiz and demonstrating competency.

**Q: Do I need access to expensive GPU resources?**
A: Most labs can be completed with cloud credits (AWS, GCP provide free tiers). Some projects require GPU access, but we provide alternatives.

**Q: How is this different from cloud provider certifications?**
A: This is vendor-neutral, focuses on production ML infrastructure specifically, and includes hands-on projects rather than just theory.

**Q: Can I use this for corporate training?**
A: Yes! The curriculum is MIT licensed. Contact us for bulk access and customization.

**Q: What comes after completing this level?**
A: The AI Infrastructure Architect curriculum (coming soon) or specialized roles in ML platform engineering.

---

## Version History

- **v1.0** (2025-10): Initial release with 10 modules and 4 projects
- More updates coming soon!

---

**Ready to level up? Start with [Module 201: Advanced Kubernetes](lessons/mod-201-advanced-kubernetes/README.md)!**

---

<!-- aicg:maintained-by -->
Maintained by [VeriSwarm.ai](https://veriswarm.ai)
