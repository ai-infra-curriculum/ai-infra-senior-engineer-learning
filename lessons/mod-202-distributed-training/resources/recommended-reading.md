# Recommended Reading: Distributed Training at Scale

## Essential Papers

### Distributed Training Fundamentals

1. **"Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour"**  
   Goyal et al., Facebook AI Research, 2017  
   [https://arxiv.org/abs/1706.02677](https://arxiv.org/abs/1706.02677)  
   Topics: Learning rate scaling, warmup, large batch training

2. **"Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"**  
   Shoeybi et al., NVIDIA, 2019  
   [https://arxiv.org/abs/1909.08053](https://arxiv.org/abs/1909.08053)  
   Topics: Tensor parallelism, intra-layer model parallelism

3. **"GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism"**  
   Huang et al., Google, 2019  
   [https://arxiv.org/abs/1811.06965](https://arxiv.org/abs/1811.06965)  
   Topics: Pipeline parallelism, micro-batching, gradient accumulation

### Memory Optimization

4. **"ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"**  
   Rajbhandari et al., Microsoft, 2020  
   [https://arxiv.org/abs/1910.02054](https://arxiv.org/abs/1910.02054)  
   Topics: ZeRO optimizer, memory partitioning, trillion-scale models

5. **"Training Deep Nets with Sublinear Memory Cost"**  
   Chen et al., 2016  
   [https://arxiv.org/abs/1604.06174](https://arxiv.org/abs/1604.06174)  
   Topics: Gradient checkpointing, memory-computation tradeoff

### Mixed Precision Training

6. **"Mixed Precision Training"**  
   Micikevicius et al., NVIDIA, 2017  
   [https://arxiv.org/abs/1710.03740](https://arxiv.org/abs/1710.03740)  
   Topics: FP16 training, loss scaling, numerical stability

7. **"A Study of BFLOAT16 for Deep Learning Training"**  
   Kalamkar et al., Intel, 2019  
   [https://arxiv.org/abs/1905.12322](https://arxiv.org/abs/1905.12322)  
   Topics: BFloat16 format, hardware support, training stability

### Communication and Networking

8. **"Horovod: Fast and Easy Distributed Deep Learning in TensorFlow"**  
   Sergeev & Del Balso, Uber, 2018  
   [https://arxiv.org/abs/1802.05799](https://arxiv.org/abs/1802.05799)  
   Topics: Ring-AllReduce, MPI-based training, Horovod architecture

9. **"PyTorch Distributed: Experiences on Accelerating Data Parallel Training"**  
   Li et al., Facebook, 2020  
   [https://arxiv.org/abs/2006.15704](https://arxiv.org/abs/2006.15704)  
   Topics: PyTorch DDP, gradient bucketing, communication optimization

### Scalability and Performance

10. **"Scaling Distributed Machine Learning with the Parameter Server"**  
    Li et al., CMU, 2014  
    [https://www.cs.cmu.edu/~muli/file/parameter_server_osdi14.pdf](https://www.cs.cmu.edu/~muli/file/parameter_server_osdi14.pdf)  
    Topics: Parameter server architecture, asynchronous SGD

11. **"1-bit Adam: Communication Efficient Large-Scale Training with Adam's Convergence Speed"**  
    Tang et al., Microsoft, 2021  
    [https://arxiv.org/abs/2102.02888](https://arxiv.org/abs/2102.02888)  
    Topics: Gradient compression, communication reduction

## Books

### Comprehensive Guides

1. **"Deep Learning"** by Ian Goodfellow, Yoshua Bengio, Aaron Courville  
   MIT Press, 2016  
   Chapter 8: Optimization for Training Deep Models  
   [https://www.deeplearningbook.org/](https://www.deeplearningbook.org/)

2. **"Parallel and Distributed Deep Learning"** by Amir Gholami et al.  
   2018  
   [https://arxiv.org/abs/1802.09941](https://arxiv.org/abs/1802.09941)

3. **"Programming Massively Parallel Processors"** by David Kirk, Wen-mei Hwu  
   Morgan Kaufmann, 4th Edition, 2022  
   GPU programming and optimization

## Technical Documentation

### Framework Documentation

1. **PyTorch Distributed**  
   [https://pytorch.org/tutorials/beginner/dist_overview.html](https://pytorch.org/tutorials/beginner/dist_overview.html)  
   Official PyTorch distributed training guide

2. **Ray Train Documentation**  
   [https://docs.ray.io/en/latest/train/train.html](https://docs.ray.io/en/latest/train/train.html)  
   Ray Train API and examples

3. **Horovod Documentation**  
   [https://horovod.readthedocs.io/](https://horovod.readthedocs.io/)  
   Complete Horovod guide with examples

4. **DeepSpeed Documentation**  
   [https://www.deepspeed.ai/](https://www.deepspeed.ai/)  
   Microsoft's training optimization library

### NVIDIA Resources

5. **NCCL Documentation**  
   [https://docs.nvidia.com/deeplearning/nccl/](https://docs.nvidia.com/deeplearning/nccl/)  
   NCCL API and optimization guide

6. **NVIDIA Deep Learning Performance Guide**  
   [https://docs.nvidia.com/deeplearning/performance/](https://docs.nvidia.com/deeplearning/performance/)  
   Best practices for GPU training

7. **Megatron-LM GitHub**  
   [https://github.com/NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM)  
   Reference implementation for large-scale training

## Blog Posts and Articles

### Industry Best Practices

1. **"Training GPT-3"** - OpenAI Blog  
   [https://openai.com/blog/gpt-3-apps](https://openai.com/blog/gpt-3-apps)  
   Insights into training 175B parameter models

2. **"How We Trained the Largest Model in the World"** - Microsoft  
   [https://www.microsoft.com/en-us/research/blog/](https://www.microsoft.com/en-us/research/blog/)  
   ZeRO and large-scale training at Microsoft

3. **"Distributed Training at Scale"** - Meta AI  
   Engineering blog on distributed training infrastructure

4. **"Efficient Deep Learning"** - Google AI Blog  
   [https://ai.googleblog.com/](https://ai.googleblog.com/)  
   Various posts on optimization and efficiency

### Technical Deep Dives

5. **"Understanding Ring-AllReduce"** - Andrew Gibiansky  
   [http://andrew.gibiansky.com/blog/machine-learning/baidu-allreduce/](http://andrew.gibiansky.com/blog/machine-learning/baidu-allreduce/)  
   Detailed explanation of Ring-AllReduce algorithm

6. **"The Case for 3D Parallelism"** - Anyscale Blog  
   [https://www.anyscale.com/blog](https://www.anyscale.com/blog)  
   Combining different parallelism strategies

7. **"Mixed Precision Training: Theory and Practice"** - NVIDIA Developer Blog  
   [https://developer.nvidia.com/blog/](https://developer.nvidia.com/blog/)  
   Practical guide to mixed precision

## Video Lectures and Tutorials

### Conference Talks

1. **"Distributed Deep Learning"** - Jeff Dean (Google), NeurIPS 2021  
   Large-scale training infrastructure at Google

2. **"Training Large Models"** - Sam Altman (OpenAI), Various conferences  
   Insights into GPT training

3. **"Ray: A Distributed Framework for Emerging AI Applications"** - Ion Stoica  
   OSDI 2018 presentation on Ray architecture

### Online Courses

4. **"Parallel Programming"** - Coursera/NVIDIA  
   GPU programming and optimization

5. **"Distributed Systems"** - MIT OpenCourseWare  
   Fundamentals of distributed computing

## Research Groups and Labs

### Leading Research Groups

1. **UC Berkeley RISELab** - [https://rise.cs.berkeley.edu/](https://rise.cs.berkeley.edu/)  
   Ray and distributed systems research

2. **Microsoft Research** - Deep Learning Group  
   ZeRO and DeepSpeed development

3. **NVIDIA Research** - Deep Learning Team  
   Megatron-LM and optimization techniques

4. **Google Brain** - [https://research.google/teams/brain/](https://research.google/teams/brain/)  
   Large-scale ML infrastructure

5. **Meta AI Research** - [https://ai.facebook.com/](https://ai.facebook.com/)  
   PyTorch and distributed training

## Benchmarks and Datasets

### MLPerf Training Benchmarks

1. **MLPerf Training Results**  
   [https://mlcommons.org/en/training-normal-11/](https://mlcommons.org/en/training-normal-11/)  
   Industry standard benchmarks for training performance

2. **NCCL Tests**  
   [https://github.com/NVIDIA/nccl-tests](https://github.com/NVIDIA/nccl-tests)  
   Benchmark communication performance

## Community Resources

### Forums and Discussion

1. **PyTorch Distributed Forum**  
   [https://discuss.pytorch.org/c/distributed](https://discuss.pytorch.org/c/distributed)  
   Community Q&A and discussions

2. **Ray Discuss**  
   [https://discuss.ray.io/](https://discuss.ray.io/)  
   Ray community forum

3. **NVIDIA Developer Forums**  
   [https://forums.developer.nvidia.com/](https://forums.developer.nvidia.com/)  
   GPU and CUDA discussions

### GitHub Repositories

4. **Awesome Distributed Training**  
   [https://github.com/topics/distributed-training](https://github.com/topics/distributed-training)  
   Curated list of distributed training resources

5. **Production ML Examples**  
   Various repositories with production-grade implementations

## Staying Current

### Conferences to Follow

1. **NeurIPS** - Neural Information Processing Systems  
2. **ICML** - International Conference on Machine Learning  
3. **MLSys** - Conference on Machine Learning and Systems  
4. **OSDI/SOSP** - Systems conferences with ML infrastructure papers

### Newsletters and Blogs

1. **The Batch** by DeepLearning.AI - Weekly AI news  
2. **Import AI** by Jack Clark - Weekly AI newsletter  
3. **Papers With Code** - Latest ML research with code

## Reading Path Recommendations

### For Beginners (Week 1-2)
1. PyTorch Distributed Tutorial
2. "Accurate, Large Minibatch SGD" paper
3. Horovod documentation and examples

### For Intermediate (Week 3-4)
1. "Megatron-LM" paper
2. "GPipe" paper
3. NCCL documentation
4. Ray Train tutorials

### For Advanced (Week 5-6)
1. "ZeRO" paper
2. Mixed precision papers
3. DeepSpeed documentation
4. Megatron-LM source code

### For Production Engineers (Ongoing)
1. NVIDIA performance guides
2. MLPerf results analysis
3. Industry blog posts
4. Framework release notes

---

**Last Updated**: 2025-10-16  
**Maintained By**: AI Infrastructure Curriculum Team

This reading list is continuously updated. Check back regularly for new resources.
