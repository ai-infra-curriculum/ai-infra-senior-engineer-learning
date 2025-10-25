# Module 206: Advanced MLOps - Quiz

## Instructions
- Answer all 30 questions
- Each question worth 1 point
- Passing score: 24/30 (80%)
- Time limit: 45 minutes

## Section 1: MLOps Maturity (6 questions)

1. What characterizes MLOps Maturity Level 0?
   a) Automated training pipelines
   b) Manual, script-driven processes
   c) CI/CD for models
   d) Feature store implementation

2. Which component is essential for Level 2 (Automated Training)?
   a) Manual model deployment
   b) Experiment tracking system
   c) No version control
   d) Ad-hoc training scripts

3. What is training-serving skew?
   a) Time difference between training and serving
   b) Difference in feature computation between training and serving
   c) Model performance degradation
   d) Infrastructure capacity mismatch

4. At what maturity level is A/B testing typically introduced?
   a) Level 0
   b) Level 1
   c) Level 2
   d) Level 3

5. Which metric indicates overfitting in production?
   a) High training accuracy, low test accuracy
   b) Low training accuracy, high test accuracy
   c) Equal training and test accuracy
   d) Negative accuracy

6. What is the primary goal of MLOps maturity assessment?
   a) Reduce model accuracy
   b) Identify gaps and plan improvements
   c) Increase team size
   d) Remove automation

## Section 2: Feature Stores (6 questions)

7. What problem do feature stores primarily solve?
   a) Model training speed
   b) Training-serving skew
   c) Data storage costs
   d) GPU utilization

8. What is point-in-time correctness?
   a) Models predict in real-time
   b) Features retrieved as they existed at specific timestamp
   c) Training completes on time
   d) Predictions have low latency

9. Which store serves features for training?
   a) Online store only
   b) Offline store only
   c) Both online and offline
   d) Neither

10. What is the purpose of feature TTL (Time-To-Live)?
    a) Model expiration
    b) Feature freshness management
    c) Training duration limit
    d) API timeout

11. In Feast, what does `materialize()` do?
    a) Deletes old features
    b) Copies features from offline to online store
    c) Trains models
    d) Deploys services

12. Why use a feature store over ad-hoc feature computation?
    a) It's slower
    b) Ensures consistency and reusability
    c) Requires more code
    d) Only works offline

## Section 3: Model Registry & Versioning (5 questions)

13. What information should a model registry track?
    a) Only model files
    b) Hyperparameters, metrics, artifacts, lineage
    c) Just accuracy scores
    d) Training logs only

14. What are the typical model stages in MLflow?
    a) New, Old, Archived
    b) None, Staging, Production, Archived
    c) Training, Testing, Production
    d) Alpha, Beta, Release

15. What is model lineage?
    a) Model performance over time
    b) Traceback to data, code, and configuration used
    c) Model deployment history
    d) User access logs

16. When should you transition a model to Production stage?
    a) Immediately after training
    b) After passing validation and approval
    c) Never
    d) When accuracy > 50%

17. What enables model reproducibility?
    a) Logging hyperparameters, data version, code version
    b) Using same hardware
    c) Training multiple times
    d) Manual documentation

## Section 4: Experiment Tracking (4 questions)

18. What should be logged in ML experiments?
    a) Only final accuracy
    b) Hyperparameters, metrics, artifacts, system info
    c) Code comments
    d) Developer names

19. What is the advantage of Bayesian optimization over grid search?
    a) Slower but more accurate
    b) Efficiently explores hyperparameter space
    c) Requires no configuration
    d) Always finds global optimum

20. Why track system resources during training?
    a) It's not necessary
    b) Understanding costs and bottlenecks
    c) GPU vendors require it
    d) Slows down training

21. What is an experiment run?
    a) Code execution duration
    b) Single execution of training with specific config
    c) Model deployment
    d) Data preprocessing step

## Section 5: A/B Testing (5 questions)

22. Why A/B test ML models?
    a) Offline metrics don't always predict online performance
    b) It's required by law
    c) Models train faster
    d) Reduces costs

23. What is statistical significance in A/B testing?
    a) Model is production-ready
    b) Observed difference unlikely due to chance
    c) Test ran long enough
    d) Traffic split is 50/50

24. How should users be assigned to variants?
    a) Randomly each request
    b) Consistently based on user ID hash
    c) Based on timestamp
    d) Alphabetically

25. What is the purpose of a multi-armed bandit?
    a) Security testing
    b) Optimize exploration vs exploitation in experiments
    c) Load testing
    d) Data validation

26. When can you conclude an A/B test?
    a) After 1 hour
    b) When statistical significance achieved with adequate sample size
    c) When boss asks
    d) Never

## Section 6: Production Systems (4 questions)

27. What is a circuit breaker pattern?
    a) Electrical safety device
    b) Prevents cascading failures by stopping calls to failing service
    c) Model retraining trigger
    d) Data validation check

28. What is graceful degradation?
    a) Model accuracy slowly declining
    b) Providing reduced functionality when primary system fails
    c) Gradual traffic increase
    d) Slow rollout

29. What triggers automated model retraining?
    a) Only manual requests
    b) Performance degradation, data drift, or schedule
    c) User complaints
    d) Random intervals

30. What is prediction drift?
    a) Latency increase
    b) Change in distribution of model predictions
    c) Feature engineering errors
    d) Database connection issues

## Answer Key
1. b  2. b  3. b  4. d  5. a
6. b  7. b  8. b  9. b  10. b
11. b  12. b  13. b  14. b  15. b
16. b  17. a  18. b  19. b  20. b
21. b  22. a  23. b  24. b  25. b
26. b  27. b  28. b  29. b  30. b
