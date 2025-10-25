# Module 203: Recommended Reading and Resources

## Official NVIDIA Documentation

### CUDA Programming

1. **CUDA C Programming Guide** (Essential)
   - URL: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
   - Topics: Complete CUDA programming reference
   - Level: Beginner to Advanced
   - Time: 20-30 hours to thoroughly read

2. **CUDA C Best Practices Guide** (Essential)
   - URL: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
   - Topics: Performance optimization techniques
   - Level: Intermediate
   - Time: 10-15 hours

3. **CUDA Runtime API Documentation**
   - URL: https://docs.nvidia.com/cuda/cuda-runtime-api/
   - Topics: API reference for CUDA functions
   - Level: All levels
   - Use: Reference material

### GPU Architecture

4. **NVIDIA Ampere GA102 GPU Architecture Whitepaper**
   - URL: https://www.nvidia.com/content/PDF/nvidia-ampere-ga-102-gpu-architecture-whitepaper-v2.pdf
   - Topics: Ampere architecture details, Tensor Cores, RT cores
   - Level: Intermediate to Advanced
   - Time: 3-4 hours

5. **NVIDIA Hopper Architecture Whitepaper**
   - URL: https://resources.nvidia.com/en-us-tensor-core
   - Topics: Hopper H100, Transformer Engine, FP8
   - Level: Advanced
   - Time: 3-4 hours

6. **NVIDIA Tesla V100 GPU Architecture Whitepaper**
   - URL: https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf
   - Topics: Volta architecture, first-gen Tensor Cores
   - Level: Intermediate
   - Time: 2-3 hours

### CUDA Libraries

7. **cuDNN Developer Guide**
   - URL: https://docs.nvidia.com/deeplearning/cudnn/
   - Topics: Deep learning primitives API
   - Level: Intermediate
   - Time: 5-8 hours

8. **cuBLAS Library Documentation**
   - URL: https://docs.nvidia.com/cuda/cublas/
   - Topics: Linear algebra operations
   - Level: Intermediate
   - Time: 3-5 hours

9. **TensorRT Developer Guide**
   - URL: https://docs.nvidia.com/deeplearning/tensorrt/
   - Topics: Inference optimization
   - Level: Intermediate to Advanced
   - Time: 10-15 hours

10. **NCCL Documentation**
    - URL: https://docs.nvidia.com/deeplearning/nccl/
    - Topics: Multi-GPU collective communications
    - Level: Intermediate
    - Time: 4-6 hours

### Profiling and Optimization

11. **Nsight Systems User Guide**
    - URL: https://docs.nvidia.com/nsight-systems/
    - Topics: System-wide profiling
    - Level: Intermediate
    - Time: 5-8 hours

12. **Nsight Compute User Guide**
    - URL: https://docs.nvidia.com/nsight-compute/
    - Topics: Kernel-level profiling
    - Level: Intermediate to Advanced
    - Time: 8-12 hours

13. **NVIDIA Deep Learning Performance Guide**
    - URL: https://docs.nvidia.com/deeplearning/performance/
    - Topics: Optimizing DL workloads
    - Level: Intermediate
    - Time: 6-10 hours

### GPU Virtualization

14. **NVIDIA Multi-Instance GPU User Guide**
    - URL: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/
    - Topics: MIG configuration and usage
    - Level: Intermediate
    - Time: 4-6 hours

15. **NVIDIA vGPU Software Documentation**
    - URL: https://docs.nvidia.com/grid/
    - Topics: GPU virtualization for VMs
    - Level: Intermediate to Advanced
    - Time: 10-15 hours

### Monitoring and Management

16. **NVIDIA DCGM User Guide**
    - URL: https://docs.nvidia.com/datacenter/dcgm/
    - Topics: GPU monitoring and management
    - Level: Intermediate
    - Time: 5-8 hours

### Cluster and System Design

17. **NVIDIA DGX Systems Documentation**
    - URL: https://docs.nvidia.com/dgx/
    - Topics: DGX A100, H100 architecture and usage
    - Level: Intermediate
    - Time: 8-12 hours

18. **NVIDIA BasePOD Reference Architecture**
    - URL: https://docs.nvidia.com/base-pod/
    - Topics: GPU cluster design
    - Level: Advanced
    - Time: 10-15 hours

19. **NVIDIA Networking Documentation**
    - URL: https://docs.nvidia.com/networking/
    - Topics: ConnectX NICs, NVSwitch, network design
    - Level: Advanced
    - Time: 10-15 hours

## Books

### Essential Books

20. **Programming Massively Parallel Processors: A Hands-on Approach** (4th Edition)
    - Authors: David B. Kirk, Wen-mei W. Hwu
    - Publisher: Morgan Kaufmann, 2022
    - Topics: Comprehensive CUDA programming
    - Level: Beginner to Intermediate
    - Why read: Best book for learning CUDA from scratch
    - Time: 40-60 hours

21. **CUDA by Example: An Introduction to General-Purpose GPU Programming**
    - Authors: Jason Sanders, Edward Kandrot
    - Publisher: Addison-Wesley, 2010
    - Topics: Practical CUDA programming with examples
    - Level: Beginner
    - Why read: Hands-on approach with working code
    - Time: 20-30 hours

22. **Professional CUDA C Programming**
    - Author: John Cheng, Max Grossman, Ty McKercher
    - Publisher: Wrox, 2014
    - Topics: Advanced CUDA optimization techniques
    - Level: Intermediate to Advanced
    - Why read: Deep dive into performance optimization
    - Time: 30-40 hours

### Parallel Computing Books

23. **Parallel Programming: Concepts and Practice**
    - Authors: Bertil Schmidt, Jorge González-Domínguez, Christian Hundt, Moritz Schlarb
    - Publisher: Morgan Kaufmann, 2017
    - Topics: Parallel programming patterns, GPU computing
    - Level: Intermediate
    - Why read: Broader context for parallel computing
    - Time: 40-50 hours

24. **Structured Parallel Programming: Patterns for Efficient Computation**
    - Authors: Michael McCool, James Reinders, Arch Robison
    - Publisher: Morgan Kaufmann, 2012
    - Topics: Parallel patterns, optimization strategies
    - Level: Intermediate
    - Why read: Pattern-based approach to parallel programming
    - Time: 30-40 hours

### ML Infrastructure Books

25. **Designing Data-Intensive Applications**
    - Author: Martin Kleppmann
    - Publisher: O'Reilly, 2017
    - Topics: System design, distributed systems
    - Level: Intermediate
    - Why read: Context for ML infrastructure design
    - Time: 40-60 hours

26. **Building Machine Learning Powered Applications**
    - Author: Emmanuel Ameisen
    - Publisher: O'Reilly, 2020
    - Topics: ML systems in production
    - Level: Intermediate
    - Why read: End-to-end ML system development
    - Time: 20-30 hours

## Academic Papers

### GPU Architecture Papers

27. **NVIDIA Tesla: A Unified Graphics and Computing Architecture** (2008)
    - Authors: Erik Lindholm et al.
    - Conference: IEEE Micro
    - Topics: GPU architecture evolution
    - Level: Advanced
    - Time: 2-3 hours

28. **Volta: Performance and Programmability** (2017)
    - Authors: NVIDIA Research
    - Topics: Volta architecture, Tensor Cores
    - Level: Advanced
    - Time: 1-2 hours

### Distributed Training Papers

29. **Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism** (2019)
    - Authors: Mohammad Shoeybi et al. (NVIDIA)
    - URL: https://arxiv.org/abs/1909.08053
    - Topics: Tensor parallelism, large model training
    - Level: Advanced
    - Time: 2-3 hours

30. **ZeRO: Memory Optimizations Toward Training Trillion Parameter Models** (2020)
    - Authors: Samyam Rajbhandari et al. (Microsoft)
    - URL: https://arxiv.org/abs/1910.02054
    - Topics: Memory optimization, data parallelism
    - Level: Advanced
    - Time: 2-3 hours

31. **GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism** (2019)
    - Authors: Yanping Huang et al. (Google)
    - URL: https://arxiv.org/abs/1811.06965
    - Topics: Pipeline parallelism
    - Level: Advanced
    - Time: 2-3 hours

### Inference Optimization Papers

32. **TensorRT: Fast and Efficient Deep Learning Inference** (2016)
    - Authors: NVIDIA Research
    - Topics: Inference optimization techniques
    - Level: Intermediate
    - Time: 1-2 hours

33. **NVIDIA TensorRT Developer Guide** (Latest)
    - Updated continuously
    - Topics: Latest TensorRT optimizations
    - Level: Intermediate to Advanced

## Online Courses and Tutorials

### NVIDIA Deep Learning Institute (DLI)

34. **Fundamentals of Accelerated Computing with CUDA C/C++**
    - Platform: NVIDIA DLI
    - URL: https://www.nvidia.com/dli
    - Duration: 8 hours
    - Cost: $90 (certificate available)
    - Level: Beginner to Intermediate

35. **Fundamentals of Deep Learning**
    - Platform: NVIDIA DLI
    - Duration: 8 hours
    - Cost: $90
    - Level: Beginner

36. **Building Transformer-Based Natural Language Processing Applications**
    - Platform: NVIDIA DLI
    - Duration: 8 hours
    - Cost: $90
    - Level: Intermediate

### Coursera

37. **GPU Programming** (Johns Hopkins University)
    - Instructor: Randal Burns
    - Duration: 4 weeks
    - Cost: Free to audit, $49 for certificate
    - Level: Intermediate

38. **Introduction to Parallel Programming** (NVIDIA/Udacity)
    - Free
    - Duration: 3 months (part-time)
    - Level: Beginner to Intermediate

### YouTube Channels

39. **NVIDIA Developer**
    - URL: https://www.youtube.com/c/NVIDIADeveloper
    - Topics: CUDA, GPU programming, GTC talks
    - Update frequency: Weekly

40. **Weights & Biases**
    - URL: https://www.youtube.com/c/WeightsBiases
    - Topics: ML engineering, distributed training
    - Update frequency: Weekly

## Blogs and Websites

### Technical Blogs

41. **NVIDIA Developer Blog**
    - URL: https://developer.nvidia.com/blog/
    - Topics: CUDA, GPU computing, AI infrastructure
    - Update frequency: 2-3 posts/week
    - Why follow: Latest NVIDIA technologies and techniques

42. **PyTorch Blog**
    - URL: https://pytorch.org/blog/
    - Topics: PyTorch features, distributed training
    - Update frequency: Monthly
    - Why follow: PyTorch best practices

43. **TensorFlow Blog**
    - URL: https://blog.tensorflow.org/
    - Topics: TensorFlow features, performance optimization
    - Update frequency: Weekly

44. **Hugging Face Blog**
    - URL: https://huggingface.co/blog
    - Topics: LLMs, model optimization, deployment
    - Update frequency: Weekly

### Company Engineering Blogs

45. **OpenAI Blog**
    - URL: https://openai.com/blog/
    - Topics: Large-scale training, GPT models
    - Why follow: Insights into training massive models

46. **Google AI Blog**
    - URL: https://ai.googleblog.com/
    - Topics: ML research, system design
    - Why follow: Cutting-edge research and infrastructure

47. **Meta AI Blog**
    - URL: https://ai.facebook.com/blog/
    - Topics: ML infrastructure, PyTorch, distributed training

48. **Microsoft Research Blog**
    - URL: https://www.microsoft.com/en-us/research/blog/
    - Topics: DeepSpeed, distributed training

## Community Resources

### Forums and Communities

49. **NVIDIA Developer Forums**
    - URL: https://forums.developer.nvidia.com/
    - Topics: CUDA, GPU programming, troubleshooting
    - Why join: Get help from NVIDIA engineers

50. **Stack Overflow - CUDA Tag**
    - URL: https://stackoverflow.com/questions/tagged/cuda
    - Topics: CUDA programming questions
    - Why join: Community Q&A

51. **r/CUDA (Reddit)**
    - URL: https://www.reddit.com/r/CUDA/
    - Topics: CUDA programming, GPU news
    - Why join: Community discussions

52. **r/MachineLearning (Reddit)**
    - URL: https://www.reddit.com/r/MachineLearning/
    - Topics: ML research, engineering, infrastructure
    - Why join: Stay current with ML trends

### Conference Proceedings

53. **NVIDIA GTC (GPU Technology Conference)**
    - URL: https://www.nvidia.com/gtc/
    - Frequency: Annual (Spring)
    - Topics: GPU computing, AI, data science
    - Why attend: Latest NVIDIA announcements, technical sessions
    - Format: In-person + virtual (many talks available on-demand)

54. **MLSys (Conference on Machine Learning and Systems)**
    - URL: https://mlsys.org/
    - Frequency: Annual
    - Topics: ML systems, infrastructure
    - Why follow: Cutting-edge ML systems research

55. **ISCA (International Symposium on Computer Architecture)**
    - URL: https://iscaconf.org/
    - Topics: Computer architecture, GPU architecture
    - Why follow: Deep hardware architecture research

## GitHub Repositories

### Example Code and Samples

56. **NVIDIA CUDA Samples**
    - URL: https://github.com/NVIDIA/cuda-samples
    - Topics: Official CUDA code samples
    - Why clone: Learn from official examples

57. **PyTorch Examples**
    - URL: https://github.com/pytorch/examples
    - Topics: PyTorch code examples
    - Why clone: Best practices for PyTorch

58. **NVIDIA Megatron-LM**
    - URL: https://github.com/NVIDIA/Megatron-LM
    - Topics: Large-scale distributed training
    - Why study: Reference implementation for model parallelism

59. **Microsoft DeepSpeed**
    - URL: https://github.com/microsoft/DeepSpeed
    - Topics: Distributed training optimization
    - Why study: ZeRO optimizer, pipeline parallelism

60. **Hugging Face Transformers**
    - URL: https://github.com/huggingface/transformers
    - Topics: Pre-trained models, distributed training
    - Why study: Industry-standard model library

## Podcasts

61. **The TWIML AI Podcast**
    - Host: Sam Charrington
    - Topics: ML/AI, infrastructure, research
    - Frequency: Weekly
    - Why listen: Interviews with ML practitioners and researchers

62. **Practical AI**
    - Hosts: Chris Benson, Daniel Whitenack
    - Topics: Applied AI, ML engineering
    - Frequency: Weekly
    - Why listen: Practical AI implementation discussions

## Reading Plan

### Month 1: CUDA Fundamentals
- CUDA C Programming Guide (Chapters 1-6)
- "CUDA by Example" (Chapters 1-8)
- CUDA Samples exploration
- Complete Lab 01 (Custom CUDA Kernels)

### Month 2: Architecture and Optimization
- Ampere/Hopper whitepapers
- CUDA C Best Practices Guide
- "Programming Massively Parallel Processors" (Chapters 5-10)
- Complete Lab 02 (Profiling and Optimization)

### Month 3: Multi-GPU and Distributed Training
- NCCL documentation
- Megatron-LM paper
- ZeRO paper
- DGX documentation
- Complete Lab 03 (MIG GPU Sharing)

### Month 4: Production and Scale
- TensorRT documentation
- DCGM documentation
- BasePOD reference architecture
- Complete Lab 04 (GPU Cluster Design)

## Staying Current

### Daily (15-30 minutes)
- Check NVIDIA Developer Blog
- Browse r/MachineLearning

### Weekly (2-3 hours)
- Read 1-2 technical blog posts
- Watch 1-2 GTC talks or conference videos
- Follow GitHub repos for updates

### Monthly (4-8 hours)
- Read 1 research paper
- Complete 1 online tutorial/course module
- Experiment with new tools/techniques

### Quarterly
- Review major conference proceedings (GTC, MLSys)
- Update knowledge with new whitepapers
- Reassess tooling and best practices

---

**This reading list provides a comprehensive foundation for mastering GPU computing and AI infrastructure. Start with the essentials and expand based on your specific interests and needs.**
