# Module 204: Advanced Model Optimization and Inference - Quiz

## Instructions

- 25 questions covering all module topics
- Multiple choice and short answer
- Passing score: 80% (20/25 correct)
- Time limit: 60 minutes
- Open notes allowed

---

## Section 1: Optimization Fundamentals (5 questions)

### Q1. Which metric is most important for real-time chatbot applications?
A) Throughput (tokens/second)  
B) Time-To-First-Token (TTFT)  
C) Total latency  
D) GPU memory usage  

**Answer:** B

**Explanation:** Chatbots require low TTFT (<300ms) for good user experience.

---

### Q2. A model achieves 2x speedup but accuracy drops from 94% to 91%. Is this acceptable?
A) Yes, always  
B) No, never  
C) Depends on the application  
D) Only if memory is reduced  

**Answer:** C

**Explanation:** Acceptability depends on use case. Medical/financial apps may reject 3% drop, while recommendation systems might accept it.

---

### Q3. What is the primary bottleneck in LLM decode phase?
A) Compute (matrix multiplication)  
B) Memory bandwidth (reading KV cache)  
C) CPU preprocessing  
D) Network latency  

**Answer:** B

**Explanation:** Decode phase is memory-bound due to reading large KV cache for each token.

---

### Q4. Which optimization provides immediate speedup without special hardware?
A) Unstructured pruning  
B) INT8 quantization  
C) Structured pruning  
D) 2:4 sparsity  

**Answer:** C

**Explanation:** Structured pruning reduces model size and works on any hardware.

---

### Q5. What is the theoretical speedup of INT8 over FP32 on NVIDIA Tensor Cores?
A) 2x  
B) 4x  
C) 8x  
D) 16x  

**Answer:** B

**Explanation:** INT8 operations are 4x faster than FP32 on Tensor Cores (theoretical).

---

## Section 2: TensorRT (4 questions)

### Q6. What does TensorRT's layer fusion optimize?
A) Accuracy  
B) Memory bandwidth  
C) Model size  
D) Batch size  

**Answer:** B

**Explanation:** Layer fusion reduces memory transfers by combining operations into single kernels.

---

### Q7. Which calibration algorithm does TensorRT use by default for INT8?
A) MinMax  
B) Percentile  
C) Entropy (KL divergence)  
D) Moving average  

**Answer:** C

**Explanation:** IInt8EntropyCalibrator2 (entropy-based) is the default and most accurate.

---

### Q8. What is an optimization profile in TensorRT?
A) Performance analysis report  
B) Configuration for dynamic shapes (min/opt/max)  
C) Layer timing information  
D) Calibration dataset  

**Answer:** B

**Explanation:** Optimization profiles define min/opt/max shapes for dynamic inputs.

---

### Q9. How many calibration samples are typically needed for TensorRT INT8?
A) 10-50  
B) 100-500  
C) 500-1000  
D) 5000-10000  

**Answer:** C

**Explanation:** 500-1000 representative samples provide good calibration without excessive time.

---

## Section 3: Quantization (5 questions)

### Q10. What is the main advantage of Quantization-Aware Training (QAT) over PTQ?
A) Faster inference  
B) Better accuracy preservation  
C) No calibration needed  
D) Smaller model size  

**Answer:** B

**Explanation:** QAT achieves better accuracy (0-0.5% drop vs 0.5-2% for PTQ).

---

### Q11. What does "fake quantization" do during QAT?
A) Simulates quantization: Q(x) then immediately DQ(Q(x))  
B) Skips quantization during training  
C) Uses INT8 arithmetic  
D) Quantizes only weights  

**Answer:** A

**Explanation:** Fake quantization simulates quantization/dequantization to train model to be robust.

---

### Q12. Per-channel quantization is typically applied to:
A) Activations  
B) Weights  
C) Biases  
D) All of the above  

**Answer:** B

**Explanation:** Per-channel quantization is standard for weights (different scale per output channel).

---

### Q13. What is the memory reduction from FP32 to INT4 quantization?
A) 2x  
B) 4x  
C) 8x  
D) 16x  

**Answer:** C

**Explanation:** FP32 (4 bytes) → INT4 (0.5 bytes) = 8x reduction.

---

### Q14. Which is more challenging: quantizing convolutions or layer normalization?
A) Convolutions  
B) Layer normalization  
C) Both equally challenging  
D) Neither is challenging  

**Answer:** B

**Explanation:** Layer normalization is numerically sensitive; often kept in higher precision.

---

## Section 4: LLM Optimization (6 questions)

### Q15. What problem does PagedAttention solve?
A) Slow attention computation  
B) KV cache memory fragmentation  
C) Low batch size  
D) Accuracy degradation  

**Answer:** B

**Explanation:** PagedAttention uses block-based memory like virtual memory to eliminate fragmentation.

---

### Q16. What is the typical KV cache size for LLaMA-70B with 2048 token sequence?
A) 500 MB  
B) 2 GB  
C) 5.4 GB  
D) 10 GB  

**Answer:** C

**Explanation:** ~2.62 MB/token × 2048 tokens ≈ 5.4 GB per sequence.

---

### Q17. How does Multi-Query Attention (MQA) reduce memory?
A) Quantizes KV cache  
B) Shares keys and values across all heads  
C) Reduces sequence length  
D) Compresses attention weights  

**Answer:** B

**Explanation:** MQA uses single shared K/V instead of separate per-head.

---

### Q18. What speedup does vLLM typically achieve over naive HuggingFace Transformers?
A) 1.5-2x  
B) 3-5x  
C) 5-10x  
D) 15-20x  

**Answer:** C

**Explanation:** vLLM achieves 5-10x throughput improvement via PagedAttention and continuous batching.

---

### Q19. In speculative decoding, what is the role of the "draft" model?
A) Final output generation  
B) Generate candidate tokens quickly  
C) Validate outputs  
D) Compress KV cache  

**Answer:** B

**Explanation:** Small draft model generates candidates fast, large model verifies in parallel.

---

### Q20. What is "continuous batching"?
A) Using very large batch sizes  
B) Batching requests continuously without waiting  
C) Running inference 24/7  
D) Batching only during prefill  

**Answer:** B

**Explanation:** Continuous batching adds/removes requests dynamically at each iteration.

---

## Section 5: Advanced Topics (5 questions)

### Q21. What does pruning "sparsity" refer to?
A) Number of zero parameters  
B) Percentage of parameters removed  
C) Model compression ratio  
D) Accuracy degradation  

**Answer:** B

**Explanation:** Sparsity = percentage of weights pruned (e.g., 70% sparsity = 70% weights removed).

---

### Q22. In knowledge distillation, "dark knowledge" refers to:
A) Hidden layers  
B) Soft probability distributions from teacher  
C) Pruned weights  
D) Quantized activations  

**Answer:** B

**Explanation:** Soft probabilities contain more information than hard labels (similarities between classes).

---

### Q23. What is the main benefit of LoRA over full fine-tuning?
A) Better accuracy  
B) Faster training  
C) 99%+ fewer trainable parameters  
D) No GPU needed  

**Answer:** C

**Explanation:** LoRA trains only low-rank adaptation matrices (0.1-1% of parameters).

---

### Q24. What is 2:4 structured sparsity?
A) 2 layers out of 4 are pruned  
B) 2 non-zero values in every 4 consecutive weights  
C) 2x4 convolutional filters  
D) Prune 2%, quantize 4-bit  

**Answer:** B

**Explanation:** 2:4 sparsity keeps exactly 2/4 values (supported by NVIDIA Ampere+).

---

### Q25. Which combination typically gives best accuracy-efficiency trade-off?
A) Heavy pruning + INT4  
B) Light pruning + INT8 + distillation  
C) No pruning + FP16  
D) Medium pruning + no quantization  

**Answer:** B

**Explanation:** Light pruning + INT8 + distillation balances accuracy and performance well.

---

## Short Answer Questions (Bonus)

### Q26. Explain the trade-off between batch size and latency.

**Answer:** Larger batch sizes increase throughput (more requests processed together) but increase latency for individual requests (waiting for batch to fill and process). Continuous batching solves this by not waiting for full batches.

---

### Q27. Why is INT8 quantization more effective on GPUs than CPUs?

**Answer:** GPUs have specialized INT8 Tensor Cores that provide 2-4x speedup over FP16. CPUs lack this specialized hardware, so INT8 speedup is smaller (memory bandwidth bound).

---

### Q28. Describe when to use TensorRT vs vLLM.

**Answer:** 
- **TensorRT**: Vision models, small Transformers, maximum performance, NVIDIA GPUs only
- **vLLM**: LLM serving, continuous batching needed, PagedAttention benefits, multi-request handling

---

## Grading

- Questions 1-25: 1 point each (25 points total)
- Bonus questions 26-28: 2 points each (6 bonus points)
- Passing: 20/25 (80%)
- Excellent: 23+/25 (92%+)

---

## Answer Key Summary

1. B  2. C  3. B  4. C  5. B  
6. B  7. C  8. B  9. C  10. B  
11. A  12. B  13. C  14. B  15. B  
16. C  17. B  18. C  19. B  20. B  
21. B  22. B  23. C  24. B  25. B  

**Module 204 Quiz Complete**
