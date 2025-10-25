# Recommended Reading - Module 208: IaC and GitOps

## Books

### Terraform

1. **Terraform: Up & Running** by Yevgeniy Brikman (3rd Edition, 2022)
   - Comprehensive guide to Terraform
   - Real-world examples and best practices
   - Covers testing and CI/CD integration
   - [Publisher Link](https://www.oreilly.com/library/view/terraform-up-and/9781098116736/)

2. **Terraform in Action** by Scott Winkler (2021)
   - Hands-on approach to infrastructure automation
   - Covers modules, state management, and workflows
   - [Publisher Link](https://www.manning.com/books/terraform-in-action)

3. **The Terraform Book** by James Turnbull (2023)
   - Comprehensive Terraform reference
   - From basics to advanced patterns
   - [Publisher Link](https://terraformbook.com/)

### GitOps

4. **GitOps and Kubernetes** by Billy Yuen, Alexander Matyushentsev, Todd Ekenstam, Jesse Suen (2021)
   - Comprehensive GitOps guide
   - ArgoCD and Flux implementations
   - Real-world case studies
   - [Publisher Link](https://www.manning.com/books/gitops-and-kubernetes)

5. **Continuous Delivery with Docker and Jenkins** by Rafal Leszko (2023)
   - CI/CD pipelines and GitOps
   - Docker and Kubernetes integration
   - [Publisher Link](https://www.packtpub.com/product/continuous-delivery-with-docker-and-jenkins-third-edition/9781803237480)

### Infrastructure as Code

6. **Infrastructure as Code** by Kief Morris (2nd Edition, 2020)
   - Principles and patterns for IaC
   - Cloud-agnostic approaches
   - Testing and validation strategies
   - [Publisher Link](https://www.oreilly.com/library/view/infrastructure-as-code/9781098114664/)

7. **Kubernetes Patterns** by Bilgin Ibryam and Roland Huß (2nd Edition, 2023)
   - Reusable patterns for Kubernetes
   - Design principles and best practices
   - [Publisher Link](https://www.oreilly.com/library/view/kubernetes-patterns-2nd/9781098131678/)

### Policy and Security

8. **Policy as Code** by Jimmy Ray (2023)
   - OPA and policy enforcement
   - Security and compliance automation
   - [Publisher Link](https://www.oreilly.com/library/view/policy-as-code/9781098139162/)

9. **Kubernetes Security and Observability** by Brendan Creane and Amit Gupta (2022)
   - Security best practices
   - Secrets management
   - Compliance automation
   - [Publisher Link](https://www.oreilly.com/library/view/kubernetes-security-and/9781098107093/)

## Official Documentation

### Terraform

- **Terraform Documentation**: https://www.terraform.io/docs
- **Terraform Registry**: https://registry.terraform.io/
- **Terraform Best Practices**: https://www.terraform-best-practices.com/
- **AWS Provider Documentation**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Terraform Module Development**: https://www.terraform.io/docs/language/modules/develop/index.html

### Pulumi

- **Pulumi Documentation**: https://www.pulumi.com/docs/
- **Pulumi Examples**: https://github.com/pulumi/examples
- **Pulumi AWS Provider**: https://www.pulumi.com/registry/packages/aws/
- **Pulumi Tutorials**: https://www.pulumi.com/tutorials/

### GitOps

- **GitOps Principles**: https://www.gitops.tech/
- **ArgoCD Documentation**: https://argo-cd.readthedocs.io/
- **FluxCD Documentation**: https://fluxcd.io/docs/
- **CNCF GitOps Working Group**: https://github.com/cncf/tag-app-delivery
- **GitOps Toolkit**: https://toolkit.fluxcd.io/

### Kubernetes

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Kustomize**: https://kustomize.io/
- **Helm Documentation**: https://helm.sh/docs/

### Testing

- **Terratest**: https://terratest.gruntwork.io/
- **Kitchen-Terraform**: https://github.com/newcontext-oss/kitchen-terraform
- **InSpec Documentation**: https://docs.chef.io/inspec/
- **Testcontainers**: https://www.testcontainers.org/

### Policy as Code

- **OPA Documentation**: https://www.openpolicyagent.org/docs/
- **Gatekeeper Documentation**: https://open-policy-agent.github.io/gatekeeper/
- **Conftest**: https://www.conftest.dev/
- **Sentinel Documentation**: https://docs.hashicorp.com/sentinel
- **OPA Policy Library**: https://github.com/open-policy-agent/library

### Secrets Management

- **Vault Documentation**: https://www.vaultproject.io/docs
- **SOPS**: https://github.com/mozilla/sops
- **Sealed Secrets**: https://github.com/bitnami-labs/sealed-secrets
- **External Secrets Operator**: https://external-secrets.io/
- **AWS Secrets Manager**: https://docs.aws.amazon.com/secretsmanager/

## Online Courses

### Terraform

1. **HashiCorp Certified: Terraform Associate** (HashiCorp Learn)
   - Official certification preparation
   - Free online course
   - https://learn.hashicorp.com/terraform

2. **Terraform on AWS** (A Cloud Guru)
   - AWS-specific Terraform training
   - Hands-on labs
   - https://acloudguru.com/

3. **Terraform Deep Dive** (Pluralsight)
   - Advanced Terraform concepts
   - Real-world scenarios
   - https://www.pluralsight.com/

### GitOps

4. **Introduction to GitOps** (CNCF)
   - Free GitOps fundamentals
   - https://www.edx.org/learn/gitops

5. **Argo CD - Declarative GitOps for Kubernetes** (Udemy)
   - ArgoCD implementation
   - Practical examples
   - https://www.udemy.com/

6. **GitOps with FluxCD** (Pluralsight)
   - FluxCD deep dive
   - Automation patterns
   - https://www.pluralsight.com/

### Kubernetes

7. **Certified Kubernetes Administrator (CKA)** (Linux Foundation)
   - Kubernetes administration
   - Hands-on labs
   - https://training.linuxfoundation.org/

## Blog Posts and Articles

### Must-Read Articles

1. **The Twelve-Factor App** - https://12factor.net/
   - Modern app development principles
   - Infrastructure patterns

2. **GitOps: Operations by Pull Request** - https://www.weave.works/blog/gitops-operations-by-pull-request
   - Original GitOps concept
   - Weaveworks

3. **Terraform at Scale** - https://www.hashicorp.com/resources/terraform-at-scale
   - Enterprise Terraform patterns
   - HashiCorp

4. **Testing Infrastructure as Code** - https://www.thoughtworks.com/insights/articles/testing-infrastructure-code
   - Testing strategies
   - ThoughtWorks

5. **Policy as Code: The Ultimate Guide** - https://www.openpolicyagent.org/docs/latest/policy-reference/
   - OPA best practices
   - Policy patterns

### Company Engineering Blogs

- **HashiCorp Blog**: https://www.hashicorp.com/blog
- **Weaveworks Blog**: https://www.weave.works/blog/
- **Google Cloud Blog (GKE)**: https://cloud.google.com/blog/products/containers-kubernetes
- **AWS Containers Blog**: https://aws.amazon.com/blogs/containers/
- **CNCF Blog**: https://www.cncf.io/blog/

## Podcasts

1. **The Cloudcast** - Weekly cloud computing discussions
   - https://www.thecloudcast.net/

2. **Kubernetes Podcast** - Official Kubernetes podcast
   - https://kubernetespodcast.com/

3. **The Stack Overflow Podcast** - Tech discussions
   - https://stackoverflow.blog/podcast/

4. **Software Engineering Daily** - DevOps and infrastructure
   - https://softwareengineeringdaily.com/

## Videos and Conferences

### YouTube Channels

1. **HashiCorp**: https://www.youtube.com/hashicorp
   - Terraform tutorials
   - Product updates

2. **CNCF**: https://www.youtube.com/c/cloudnativefdn
   - KubeCon talks
   - Community meetings

3. **DevOps Toolkit**: https://www.youtube.com/c/DevOpsToolkit
   - Practical DevOps content
   - Tool reviews

### Conference Talks

1. **HashiConf** - https://hashiconf.com/
   - Annual HashiCorp conference
   - Terraform best practices

2. **KubeCon + CloudNativeCon** - https://www.cncf.io/kubecon-cloudnativecon-events/
   - Largest Kubernetes conference
   - GitOps and cloud native

3. **DevOps Enterprise Summit** - https://events.itrevolution.com/
   - Enterprise DevOps
   - Case studies

## GitHub Repositories

### Example Repositories

1. **Terraform AWS Examples**: https://github.com/terraform-aws-modules
2. **ArgoCD Examples**: https://github.com/argoproj/argocd-example-apps
3. **FluxCD Examples**: https://github.com/fluxcd/flux2-kustomize-helm-example
4. **OPA Examples**: https://github.com/open-policy-agent/opa/tree/main/examples
5. **Terratest Examples**: https://github.com/gruntwork-io/terratest/tree/master/examples

### Awesome Lists

1. **Awesome Terraform**: https://github.com/shuaibiyy/awesome-terraform
2. **Awesome Kubernetes**: https://github.com/ramitsurana/awesome-kubernetes
3. **Awesome GitOps**: https://github.com/weaveworks/awesome-gitops
4. **Awesome Policy as Code**: https://github.com/policy-as-code/awesome-policy-as-code

## Community Resources

### Forums and Discussion

- **Terraform Discuss**: https://discuss.hashicorp.com/c/terraform-core
- **Kubernetes Slack**: https://kubernetes.slack.com/
- **ArgoCD Slack**: https://argoproj.github.io/community/join-slack/
- **CNCF Slack**: https://slack.cncf.io/
- **Reddit r/terraform**: https://reddit.com/r/terraform
- **Reddit r/kubernetes**: https://reddit.com/r/kubernetes

### Mailing Lists

- **CNCF GitOps WG**: https://lists.cncf.io/g/cncf-gitops-wg
- **Kubernetes Dev**: https://groups.google.com/forum/#!forum/kubernetes-dev

## Certifications

1. **HashiCorp Certified: Terraform Associate**
   - Official Terraform certification
   - https://www.hashicorp.com/certification/terraform-associate

2. **Certified Kubernetes Administrator (CKA)**
   - Kubernetes administration cert
   - https://www.cncf.io/certification/cka/

3. **Certified Kubernetes Application Developer (CKAD)**
   - Kubernetes development cert
   - https://www.cncf.io/certification/ckad/

4. **AWS Certified DevOps Engineer**
   - AWS DevOps certification
   - https://aws.amazon.com/certification/certified-devops-engineer-professional/

## Newsletters

1. **Terraform Weekly**: https://www.terraform.io/newsletter
2. **KubeWeekly**: https://www.cncf.io/kubeweekly/
3. **DevOps Weekly**: https://www.devopsweekly.com/
4. **SRE Weekly**: https://sreweekly.com/

## Tools to Explore

### Infrastructure as Code
- Terraform, Pulumi, CloudFormation, CDK

### GitOps
- ArgoCD, FluxCD, Jenkins X

### Testing
- Terratest, Kitchen-Terraform, Inspec

### Policy
- OPA, Gatekeeper, Conftest, Sentinel

### Secrets
- Vault, SOPS, Sealed Secrets, External Secrets Operator

---

**Note**: Links and resources are subject to change. Always verify the latest documentation from official sources.

**Last Updated**: October 2025
