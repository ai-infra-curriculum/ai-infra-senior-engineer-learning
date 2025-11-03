# Lecture 6: Privacy-Preserving ML

## Learning Objectives

By the end of this lecture, you will be able to:

- Design differential privacy implementations adding calibrated noise to ML training protecting individual privacy while maintaining model utility
- Implement federated learning architectures training models across decentralized data sources without centralized data aggregation preserving data locality
- Architect homomorphic encryption solutions enabling computation on encrypted data for privacy-sensitive ML inference without decryption
- Configure secure multi-party computation (MPC) for collaborative ML training multiple parties computing jointly without revealing private inputs
- Design synthetic data generation using GANs or statistical methods creating privacy-preserving datasets for development and testing
- Implement privacy budgeting and tracking with (ε, δ)-differential privacy calculating cumulative privacy loss and enforcing privacy bounds
- Build privacy-preserving inference systems with secure enclaves (SGX), trusted execution environments, or encrypted predictions
- Architect privacy compliance workflows with consent management, privacy impact assessments, data minimization, and privacy-by-design principles

## Table of Contents
1. [Introduction to Privacy-Preserving ML](#introduction)
2. [Differential Privacy](#differential-privacy)
3. [Federated Learning](#federated-learning)
4. [Homomorphic Encryption](#homomorphic-encryption)
5. [Secure Multi-Party Computation](#secure-multi-party-computation)
6. [Synthetic Data Generation](#synthetic-data-generation)
7. [Implementation Patterns](#implementation-patterns)

## Introduction

Privacy-preserving machine learning enables training models on sensitive data while protecting individual privacy. These techniques are essential for regulated industries and privacy-conscious organizations.

### Privacy Threats in ML

1. **Membership Inference**: Determining if specific data was in training set
2. **Model Inversion**: Reconstructing training data from model
3. **Attribute Inference**: Inferring sensitive attributes
4. **Model Extraction**: Stealing model through queries

### Privacy-Preserving Techniques Overview

```
┌─────────────────────────────────────────────────────────────┐
│      Privacy-Preserving ML Techniques Comparison             │
├─────────────────────────────────────────────────────────────┤
│ Technique              │ Privacy  │ Utility  │ Complexity   │
│                        │ Level    │ Loss     │              │
├────────────────────────┼──────────┼──────────┼──────────────┤
│ Differential Privacy   │ High     │ Low-Med  │ Medium       │
│ Federated Learning     │ Medium   │ Low      │ High         │
│ Homomorphic Encryption │ Very High│ None     │ Very High    │
│ Secure MPC             │ Very High│ None     │ Very High    │
│ Synthetic Data         │ Medium   │ Medium   │ Medium       │
└─────────────────────────────────────────────────────────────┘
```

## Differential Privacy

Differential privacy provides mathematical guarantees that individual data points don't significantly affect outputs.

### DP Fundamentals

**Definition**: A mechanism M is ε-differentially private if for all datasets D1 and D2 differing by one record:

```
P[M(D1) ∈ S] ≤ e^ε * P[M(D2) ∈ S]
```

**Epsilon (ε)**: Privacy budget (lower = more private)
- ε < 1: Strong privacy
- ε = 1: Reasonable privacy
- ε > 10: Weak privacy

### Implementing Differential Privacy

```python
import numpy as np
from typing import List, Tuple

class DifferentialPrivacy:
    """Differential privacy mechanisms"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
    
    def laplace_mechanism(self, true_value: float, sensitivity: float) -> float:
        """
        Add Laplace noise for differential privacy
        
        Args:
            true_value: Real value to privatize
            sensitivity: Maximum change from adding/removing one record
        
        Returns:
            Privatized value
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return true_value + noise
    
    def gaussian_mechanism(self, true_value: float, sensitivity: float) -> float:
        """
        Gaussian mechanism for (ε, δ)-differential privacy
        
        More efficient than Laplace for (ε, δ)-DP
        """
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma)
        return true_value + noise
    
    def randomized_response(self, true_answer: bool, p: float = 0.5) -> bool:
        """
        Randomized response for boolean answers
        
        Local differential privacy technique
        """
        # Flip coin with probability p
        if np.random.random() < p:
            return true_answer
        else:
            return not true_answer

# Example: Private statistics
class PrivateStatistics:
    """Compute statistics with differential privacy"""
    
    def __init__(self, epsilon: float = 1.0):
        self.dp = DifferentialPrivacy(epsilon=epsilon)
    
    def private_mean(self, data: np.ndarray, bounds: Tuple[float, float]) -> float:
        """
        Compute mean with differential privacy
        
        Args:
            data: Dataset
            bounds: Known bounds (min, max) for clipping
        """
        # Clip data to bounds (sensitivity reduction)
        clipped = np.clip(data, bounds[0], bounds[1])
        
        # Compute true mean
        true_mean = np.mean(clipped)
        
        # Sensitivity: (max - min) / n
        sensitivity = (bounds[1] - bounds[0]) / len(data)
        
        # Add noise
        private_mean = self.dp.laplace_mechanism(true_mean, sensitivity)
        
        return private_mean
    
    def private_count(self, data: List[bool]) -> float:
        """Count with differential privacy"""
        true_count = sum(data)
        
        # Sensitivity of count is 1
        private_count = self.dp.laplace_mechanism(true_count, sensitivity=1)
        
        return max(0, private_count)  # Ensure non-negative

# Example usage
data = np.array([25, 30, 35, 40, 45, 50, 55, 60])
stats = PrivateStatistics(epsilon=1.0)

private_avg = stats.private_mean(data, bounds=(0, 100))
print(f"Private average age: {private_avg:.1f}")
```

### DP-SGD: Training with Differential Privacy

```python
class DPSGDTrainer:
    """Differentially private stochastic gradient descent"""
    
    def __init__(
        self, 
        model, 
        epsilon: float = 1.0,
        delta: float = 1e-5,
        clip_norm: float = 1.0,
        noise_multiplier: float = 1.1
    ):
        self.model = model
        self.epsilon = epsilon
        self.delta = delta
        self.clip_norm = clip_norm
        self.noise_multiplier = noise_multiplier
    
    def train_step(self, batch_data, batch_labels):
        """
        One training step with DP-SGD
        
        Algorithm:
        1. Compute per-example gradients
        2. Clip each gradient to bound sensitivity
        3. Aggregate clipped gradients
        4. Add calibrated noise
        5. Update model
        """
        per_example_grads = []
        
        # 1 & 2: Compute and clip per-example gradients
        for data, label in zip(batch_data, batch_labels):
            grad = self.compute_gradient(data, label)
            clipped_grad = self.clip_gradient(grad, self.clip_norm)
            per_example_grads.append(clipped_grad)
        
        # 3: Aggregate
        avg_grad = np.mean(per_example_grads, axis=0)
        
        # 4: Add noise for privacy
        noise_scale = self.clip_norm * self.noise_multiplier / len(batch_data)
        noise = np.random.normal(0, noise_scale, size=avg_grad.shape)
        private_grad = avg_grad + noise
        
        # 5: Update model
        self.update_model(private_grad)
        
        return private_grad
    
    def clip_gradient(self, gradient: np.ndarray, max_norm: float) -> np.ndarray:
        """Clip gradient norm to max_norm"""
        grad_norm = np.linalg.norm(gradient)
        if grad_norm > max_norm:
            return gradient * (max_norm / grad_norm)
        return gradient
    
    def compute_privacy_spent(self, steps: int, batch_size: int, dataset_size: int) -> float:
        """
        Calculate privacy budget spent using moments accountant
        
        Returns epsilon value after training
        """
        from scipy import optimize
        
        # Sampling probability
        q = batch_size / dataset_size
        
        # Use privacy amplification by sampling
        # Simplified - actual implementation more complex
        epsilon_per_step = q * steps * (np.exp(self.noise_multiplier ** 2) - 1)
        
        return epsilon_per_step

# Example: Training with privacy
trainer = DPSGDTrainer(
    model=my_model,
    epsilon=3.0,  # Privacy budget
    delta=1e-5,
    clip_norm=1.0,
    noise_multiplier=1.1
)

for epoch in range(num_epochs):
    for batch in dataloader:
        trainer.train_step(batch.data, batch.labels)

epsilon_spent = trainer.compute_privacy_spent(
    steps=total_steps,
    batch_size=32,
    dataset_size=10000
)

print(f"Privacy budget spent: ε = {epsilon_spent:.2f}")
```

## Federated Learning

Federated learning trains models across decentralized devices without centralizing data.

### Federated Averaging (FedAvg)

```python
class FederatedServer:
    """Federated learning server"""
    
    def __init__(self, global_model):
        self.global_model = global_model
        self.round_num = 0
    
    def federated_round(self, clients: List['FederatedClient'], fraction: float = 1.0):
        """
        One round of federated learning
        
        1. Select clients
        2. Send global model to clients
        3. Clients train locally
        4. Aggregate client updates
        5. Update global model
        """
        # 1: Select subset of clients
        num_selected = int(len(clients) * fraction)
        selected_clients = np.random.choice(clients, num_selected, replace=False)
        
        # 2 & 3: Clients train locally
        client_weights = []
        client_sizes = []
        
        for client in selected_clients:
            # Send global model
            client.receive_model(self.global_model)
            
            # Client trains locally
            weights, data_size = client.local_train(epochs=1)
            
            client_weights.append(weights)
            client_sizes.append(data_size)
        
        # 4: Weighted aggregation
        total_size = sum(client_sizes)
        new_weights = {}
        
        for layer_name in self.global_model.keys():
            weighted_sum = sum(
                w[layer_name] * (size / total_size)
                for w, size in zip(client_weights, client_sizes)
            )
            new_weights[layer_name] = weighted_sum
        
        # 5: Update global model
        self.global_model = new_weights
        self.round_num += 1
        
        return self.global_model
    
    def train(self, clients: List, num_rounds: int):
        """Train for multiple federated rounds"""
        for round in range(num_rounds):
            print(f"Federated round {round + 1}/{num_rounds}")
            self.federated_round(clients)
            
            # Evaluate global model
            accuracy = self.evaluate_global_model()
            print(f"  Global model accuracy: {accuracy:.3f}")

class FederatedClient:
    """Federated learning client (edge device, hospital, etc.)"""
    
    def __init__(self, client_id: str, local_data, local_labels):
        self.client_id = client_id
        self.local_data = local_data
        self.local_labels = local_labels
        self.model = None
    
    def receive_model(self, global_model):
        """Receive global model from server"""
        self.model = global_model.copy()
    
    def local_train(self, epochs: int = 1) -> Tuple[Dict, int]:
        """
        Train on local data
        
        Data never leaves device
        """
        for epoch in range(epochs):
            # Standard training on local data
            for batch in self.local_dataloader():
                self.train_step(batch)
        
        # Return updated weights and data size
        return self.model, len(self.local_data)

# Example: Federated learning across hospitals
hospitals = [
    FederatedClient("hospital_1", hospital_1_data, hospital_1_labels),
    FederatedClient("hospital_2", hospital_2_data, hospital_2_labels),
    FederatedClient("hospital_3", hospital_3_data, hospital_3_labels),
]

server = FederatedServer(global_model=initial_model)
server.train(clients=hospitals, num_rounds=100)
```

### Secure Aggregation

Prevent server from seeing individual updates:

```python
class SecureAggregation:
    """Secure aggregation for federated learning"""
    
    def __init__(self, num_clients: int):
        self.num_clients = num_clients
        self.client_secrets = {}
    
    def generate_pairwise_masks(self, client_id: int):
        """
        Generate pairwise masks for secure aggregation
        
        Clients share pairwise secrets to create masks that cancel out
        """
        masks = []
        
        for other_id in range(self.num_clients):
            if other_id == client_id:
                continue
            
            # Generate or retrieve shared secret
            if (client_id, other_id) in self.client_secrets:
                secret = self.client_secrets[(client_id, other_id)]
            elif (other_id, client_id) in self.client_secrets:
                secret = -self.client_secrets[(other_id, client_id)]
            else:
                secret = np.random.randn()
                self.client_secrets[(client_id, other_id)] = secret
            
            masks.append(secret)
        
        return np.array(masks).sum()
    
    def masked_model_update(self, client_id: int, model_update):
        """
        Client masks their model update
        
        Only aggregated result visible to server
        """
        mask = self.generate_pairwise_masks(client_id)
        masked_update = model_update + mask
        return masked_update
    
    def aggregate(self, masked_updates):
        """
        Server aggregates masked updates
        
        Masks cancel out, leaving sum of true updates
        """
        # Sum of all masked updates
        # Pairwise masks cancel: (secret_ij - secret_ji) = 0
        return sum(masked_updates)

# Example
secure_agg = SecureAggregation(num_clients=3)

# Clients mask their updates
masked_1 = secure_agg.masked_model_update(0, update_1)
masked_2 = secure_agg.masked_model_update(1, update_2)
masked_3 = secure_agg.masked_model_update(2, update_3)

# Server aggregates without seeing individual updates
aggregated = secure_agg.aggregate([masked_1, masked_2, masked_3])
# aggregated = update_1 + update_2 + update_3
```

## Homomorphic Encryption

Homomorphic encryption allows computation on encrypted data without decryption.

### Partially Homomorphic Encryption

```python
from phe import paillier

class HomomorphicMLInference:
    """ML inference on encrypted data"""
    
    def __init__(self):
        # Generate encryption keys
        self.public_key, self.private_key = paillier.generate_paillier_keypair()
    
    def encrypt_features(self, features: np.ndarray) -> List:
        """Encrypt input features"""
        encrypted = [self.public_key.encrypt(float(x)) for x in features]
        return encrypted
    
    def encrypted_linear_model(
        self, 
        encrypted_features: List, 
        weights: np.ndarray, 
        bias: float
    ):
        """
        Compute linear model on encrypted data
        
        y = w^T x + b
        
        Performed entirely on encrypted values
        """
        # Encrypted weighted sum
        encrypted_result = self.public_key.encrypt(bias)
        
        for enc_x, w in zip(encrypted_features, weights):
            # Homomorphic operation: enc(x) * w = enc(w * x)
            encrypted_result += enc_x * w
        
        return encrypted_result
    
    def decrypt_result(self, encrypted_result):
        """Decrypt prediction"""
        return self.private_key.decrypt(encrypted_result)

# Example: Private inference
he_inference = HomomorphicMLInference()

# Client encrypts sensitive medical data
patient_features = np.array([65, 180, 75, 120, 80])  # age, height, weight, BP
encrypted_features = he_inference.encrypt_features(patient_features)

# Server computes on encrypted data (can't see actual values)
model_weights = np.array([0.1, 0.05, 0.2, 0.3, -0.1])
bias = 2.0

encrypted_prediction = he_inference.encrypted_linear_model(
    encrypted_features,
    model_weights,
    bias
)

# Only client can decrypt result
prediction = he_inference.decrypt_result(encrypted_prediction)
print(f"Risk score: {prediction:.2f}")
```

## Secure Multi-Party Computation

MPC allows multiple parties to compute functions on private inputs without revealing them.

### Secret Sharing

```python
class SecretSharing:
    """Additive secret sharing for MPC"""
    
    def share_secret(self, secret: float, num_shares: int) -> List[float]:
        """
        Split secret into shares
        
        Sum of shares = secret
        """
        shares = [np.random.randn() for _ in range(num_shares - 1)]
        last_share = secret - sum(shares)
        shares.append(last_share)
        return shares
    
    def reconstruct_secret(self, shares: List[float]) -> float:
        """Reconstruct secret from shares"""
        return sum(shares)
    
    def secure_addition(
        self, 
        shares_a: List[float], 
        shares_b: List[float]
    ) -> List[float]:
        """
        Add two secret-shared values
        
        Each party adds their shares locally
        """
        return [a + b for a, b in zip(shares_a, shares_b)]
    
    def secure_multiplication(
        self,
        shares_a: List[float],
        shares_b: List[float]
    ) -> List[float]:
        """
        Multiply two secret-shared values
        
        More complex - requires communication
        """
        # Simplified - actual secure multiplication more involved
        num_parties = len(shares_a)
        
        # Each party computes local products
        local_products = [a * b for a, b in zip(shares_a, shares_b)]
        
        # Re-share products
        result_shares = []
        for product in local_products:
            new_shares = self.share_secret(product, num_parties)
            if not result_shares:
                result_shares = new_shares
            else:
                result_shares = [r + n for r, n in zip(result_shares, new_shares)]
        
        return result_shares

# Example: Secure aggregation of private data
ss = SecretSharing()

# Three hospitals want to compute average salary without revealing individual salaries
hospital_1_salary = 75000
hospital_2_salary = 80000
hospital_3_salary = 85000

# Each hospital secret-shares their value
shares_1 = ss.share_secret(hospital_1_salary, 3)
shares_2 = ss.share_secret(hospital_2_salary, 3)
shares_3 = ss.share_secret(hospital_3_salary, 3)

# Parties securely add their shares
total_shares = ss.secure_addition(shares_1, shares_2)
total_shares = ss.secure_addition(total_shares, shares_3)

# Reconstruct total (can be done by trusted party or threshold)
total_salary = ss.reconstruct_secret(total_shares)
average = total_salary / 3

print(f"Average salary (computed securely): ${average:,.0f}")
```

## Synthetic Data Generation

Generate realistic synthetic data that preserves statistical properties without revealing individuals.

### Differentially Private Synthetic Data

```python
class DPSyntheticDataGenerator:
    """Generate DP synthetic data"""
    
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon
        self.dp = DifferentialPrivacy(epsilon=epsilon)
    
    def fit(self, real_data: pd.DataFrame):
        """Learn distribution from real data"""
        # Compute DP statistics
        self.column_stats = {}
        
        for column in real_data.columns:
            if real_data[column].dtype in ['int64', 'float64']:
                # Numeric column
                mean = self.dp.laplace_mechanism(
                    real_data[column].mean(),
                    sensitivity=1.0
                )
                std = self.dp.laplace_mechanism(
                    real_data[column].std(),
                    sensitivity=1.0
                )
                self.column_stats[column] = {
                    'type': 'numeric',
                    'mean': mean,
                    'std': std
                }
            else:
                # Categorical column
                value_counts = real_data[column].value_counts()
                
                # Add DP noise to counts
                noisy_counts = {}
                for value, count in value_counts.items():
                    noisy_count = self.dp.laplace_mechanism(count, sensitivity=1.0)
                    noisy_counts[value] = max(0, noisy_count)
                
                # Normalize to probabilities
                total = sum(noisy_counts.values())
                probabilities = {k: v/total for k, v in noisy_counts.items()}
                
                self.column_stats[column] = {
                    'type': 'categorical',
                    'probabilities': probabilities
                }
    
    def generate(self, n_samples: int) -> pd.DataFrame:
        """Generate synthetic data"""
        synthetic_data = {}
        
        for column, stats in self.column_stats.items():
            if stats['type'] == 'numeric':
                # Sample from normal distribution
                synthetic_data[column] = np.random.normal(
                    stats['mean'],
                    stats['std'],
                    n_samples
                )
            else:
                # Sample from categorical distribution
                values = list(stats['probabilities'].keys())
                probs = list(stats['probabilities'].values())
                synthetic_data[column] = np.random.choice(
                    values,
                    n_samples,
                    p=probs
                )
        
        return pd.DataFrame(synthetic_data)

# Example usage
real_data = pd.DataFrame({
    'age': [25, 30, 35, 40, 45],
    'income': [50000, 60000, 70000, 80000, 90000],
    'city': ['NYC', 'SF', 'NYC', 'LA', 'SF']
})

generator = DPSyntheticDataGenerator(epsilon=1.0)
generator.fit(real_data)

# Generate synthetic data (privacy-preserving)
synthetic_data = generator.generate(n_samples=1000)
```

## Summary

Privacy-preserving ML techniques enable training on sensitive data while protecting privacy:

1. **Differential Privacy**: Mathematical privacy guarantees, DP-SGD for training
2. **Federated Learning**: Decentralized training, data stays on devices
3. **Homomorphic Encryption**: Computation on encrypted data
4. **Secure MPC**: Multi-party computation without revealing inputs  
5. **Synthetic Data**: Generate realistic data without exposing individuals

Choose techniques based on threat model, privacy requirements, and performance constraints.

## Resources

- [Google's Differential Privacy Library](https://github.com/google/differential-privacy)
- [TensorFlow Federated](https://www.tensorflow.org/federated)
- [Microsoft SEAL (Homomorphic Encryption)](https://github.com/microsoft/SEAL)
- [MP-SPDZ (Secure MPC)](https://github.com/data61/MP-SPDZ)

## Next Steps

- Complete Module 209 labs
- Explore privacy-preserving ML in your domain
- Continue to Module 210: Technical Leadership
