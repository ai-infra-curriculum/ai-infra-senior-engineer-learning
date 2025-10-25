# Recommended Reading - Module 204

## Essential Papers

### Quantization

1. **"Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference"** (Google, 2018)
   - Foundational paper on INT8 quantization
   - Post-training and quantization-aware training
   - https://arxiv.org/abs/1712.05877

2. **"LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale"** (Dettmers et al., 2022)
   - INT8 quantization for large language models
   - Mixed-precision decomposition
   - https://arxiv.org/abs/2208.07339

3. **"GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers"** (2022)
   - INT4 quantization for LLMs
   - Layer-wise quantization
   - https://arxiv.org/abs/2210.17323

4. **"AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration"** (2023)
   - Improved INT4 quantization
   - Better accuracy preservation
   - https://arxiv.org/abs/2306.00978

### Pruning and Compression

5. **"The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks"** (Frankle & Carbin, 2019)
   - Iterative magnitude pruning
   - Winning tickets
   - https://arxiv.org/abs/1803.03635

6. **"What is the State of Neural Network Pruning?"** (Blalock et al., 2020)
   - Comprehensive survey of pruning methods
   - Evaluation of techniques
   - https://arxiv.org/abs/2003.03033

7. **"Movement Pruning: Adaptive Sparsity by Fine-Tuning"** (Sanh et al., 2020)
   - Dynamic pruning during training
   - Better accuracy than magnitude-based
   - https://arxiv.org/abs/2005.07683

### Knowledge Distillation

8. **"Distilling the Knowledge in a Neural Network"** (Hinton et al., 2015)
   - Original knowledge distillation paper
   - Temperature-based softening
   - https://arxiv.org/abs/1503.02531

9. **"DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter"** (Sanh et al., 2019)
   - Distillation for Transformers
   - 40% size reduction with 97% performance
   - https://arxiv.org/abs/1910.01108

### LLM Inference Optimization

10. **"Efficient Memory Management for Large Language Model Serving with PagedAttention"** (vLLM paper, 2023)
    - PagedAttention algorithm
    - Continuous batching
    - https://arxiv.org/abs/2309.06180

11. **"FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"** (Dao et al., 2022)
    - Memory-efficient attention
    - 2-4x speedup
    - https://arxiv.org/abs/2205.14135

12. **"Fast Inference from Transformers via Speculative Decoding"** (Leviathan et al., 2023)
    - Speculative decoding technique
    - 2-3x speedup for LLM generation
    - https://arxiv.org/abs/2211.17192

13. **"GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"** (Ainslie et al., 2023)
    - Grouped-Query Attention
    - Memory-efficient attention variant
    - https://arxiv.org/abs/2305.13245

## Technical Documentation

### TensorRT

- **NVIDIA TensorRT Documentation**: https://docs.nvidia.com/deeplearning/tensorrt/
- **TensorRT Developer Guide**: https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/
- **TensorRT Best Practices**: https://docs.nvidia.com/deeplearning/tensorrt/best-practices/
- **TensorRT Python API**: https://docs.nvidia.com/deeplearning/tensorrt/api/python_api/

### ONNX Runtime

- **ONNX Runtime Documentation**: https://onnxruntime.ai/docs/
- **ONNX Runtime Performance Tuning**: https://onnxruntime.ai/docs/performance/
- **Execution Providers**: https://onnxruntime.ai/docs/execution-providers/
- **Quantization in ONNX Runtime**: https://onnxruntime.ai/docs/performance/quantization.html

### vLLM

- **vLLM Documentation**: https://docs.vllm.ai/
- **vLLM GitHub**: https://github.com/vllm-project/vllm
- **vLLM Blog**: Technical blog posts on optimization techniques

### PyTorch

- **PyTorch Quantization**: https://pytorch.org/docs/stable/quantization.html
- **PyTorch Mobile Optimization**: https://pytorch.org/mobile/home/
- **TorchScript**: https://pytorch.org/docs/stable/jit.html

## Books

1. **"Efficient Deep Learning"** by Gaurav Menghani
   - Comprehensive guide to model optimization
   - Covers quantization, pruning, distillation
   - Practical techniques and case studies

2. **"Deep Learning Inference: Optimizing Neural Networks for Production"** by Sriraman et al.
   - Production deployment focus
   - Hardware-specific optimizations
   - Real-world case studies

3. **"Machine Learning Systems: Design and Implementation"** (Stanford CS 329S)
   - ML systems design
   - Inference optimization chapter
   - Available online free

## Blog Posts and Tutorials

### Must-Read Blogs

1. **Hugging Face Blog**: https://huggingface.co/blog
   - Regular posts on optimization techniques
   - Model compression tutorials
   - LLM inference optimization

2. **NVIDIA Developer Blog**: https://developer.nvidia.com/blog
   - TensorRT tutorials
   - GPU optimization techniques
   - Latest hardware features

3. **Google AI Blog**: https://ai.googleblog.com/
   - Research announcements
   - Quantization techniques
   - TPU optimizations

4. **Meta AI Blog**: https://ai.facebook.com/blog/
   - LLM optimization
   - Production deployment
   - PyTorch optimizations

### Specific Tutorials

- **"A Gentle Introduction to INT8 Quantization"** (Lei Mao)
  - Excellent quantization primer
  - Mathematical foundations
  - https://leimao.github.io/blog/

- **"Making Deep Learning Go Brrrr From First Principles"** (Horace He)
  - GPU performance optimization
  - Memory bandwidth analysis
  - https://horace.io/brrr_intro.html

- **"Transformer Inference Arithmetic"** (Kipply)
  - LLM inference cost analysis
  - KV cache memory calculations
  - https://kipp.ly/transformer-inference-arithmetic/

## Online Courses

1. **"Efficient Deep Learning Systems"** (MIT 6.5940)
   - Free online course
   - Model compression, quantization, pruning
   - https://efficientml.ai/

2. **"TinyML and Efficient Deep Learning Computing"** (MIT)
   - Edge deployment
   - Extreme optimization techniques
   - Available on YouTube

3. **"Full Stack Deep Learning"** (FSDL)
   - Production ML systems
   - Inference optimization module
   - https://fullstackdeeplearning.com/

## Benchmarks and Leaderboards

1. **MLPerf Inference**: https://mlcommons.org/en/inference/
   - Industry-standard benchmarks
   - Compare techniques and hardware
   - Submission requirements

2. **ONNX Model Zoo**: https://github.com/onnx/models
   - Pre-optimized models
   - Benchmark baselines
   - Multiple frameworks

3. **Papers with Code**: https://paperswithcode.com/
   - Latest research with implementations
   - Benchmark results
   - Leaderboards

## GitHub Repositories

### Essential Repos

1. **TensorRT Examples**: https://github.com/NVIDIA/TensorRT
2. **ONNX Runtime**: https://github.com/microsoft/onnxruntime
3. **vLLM**: https://github.com/vllm-project/vllm
4. **PyTorch Quantization**: https://github.com/pytorch/pytorch/tree/master/torch/quantization
5. **Brevitas** (QAT framework): https://github.com/Xilinx/brevitas
6. **Neural Compressor**: https://github.com/intel/neural-compressor
7. **GPTQ**: https://github.com/IST-DASLab/gptq
8. **AWQ**: https://github.com/mit-han-lab/llm-awq
9. **SGLang**: https://github.com/sgl-project/sglang
10. **TensorRT-LLM**: https://github.com/NVIDIA/TensorRT-LLM

## Research Groups and Labs

- **NVIDIA AI Research**: https://www.nvidia.com/en-us/research/
- **MIT HAN Lab**: https://hanlab.mit.edu/ (TinyML, EfficientML)
- **Stanford DAWN**: https://dawn.cs.stanford.edu/ (ML systems)
- **UC Berkeley Sky Lab**: https://sky.cs.berkeley.edu/ (ML systems)

## Conferences

- **MLSys**: Machine Learning and Systems
- **SysML**: Systems for ML
- **NeurIPS**: Systems and Optimization tracks
- **ICML**: Efficient ML workshops
- **ICLR**: Model compression papers

## Community Resources

- **Reddit r/MachineLearning**: Active discussions on optimization
- **Hacker News**: ML systems discussions
- **Discord/Slack Communities**:
  - vLLM Discord
  - HuggingFace Discord
  - PyTorch Slack
  - ONNX Community

## Staying Current

### Weekly Newsletters

- **Papers with Code Weekly**
- **The Batch** (DeepLearning.AI)
- **TLDR AI**: Daily AI news
- **Import AI**: Weekly AI updates

### Twitter/X Follows

- @karpathy (Andrej Karpathy)
- @soumithchintala (Soumith Chintala, PyTorch)
- @rohanpaul_ai (Rohan Paul, ML Systems)
- @_inesmontani (Ines Montani, spaCy/ML)
- @jeremyphoward (Jeremy Howard, fast.ai)

## Reading Schedule Recommendation

### Week 1: Foundations
- Papers 1, 10, 11 (Quantization & Attention)
- TensorRT Documentation (basics)

### Week 2: Quantization Deep Dive
- Papers 2, 3, 4 (LLM quantization)
- PyTorch Quantization docs

### Week 3: Pruning and Distillation
- Papers 5, 6, 7, 8, 9
- Hugging Face distillation tutorials

### Week 4: LLM Inference
- Papers 12, 13 (Speculative decoding, GQA)
- vLLM documentation
- "Transformer Inference Arithmetic" blog

### Ongoing
- Subscribe to newsletters
- Follow MLSys conference
- Read new papers on Papers with Code

---

**Note**: This list is curated for senior-level engineers. All papers are freely available on arXiv unless otherwise noted.
