# Lecture 02: Feature Stores

## Learning Objectives

By the end of this lecture, you will be able to:

- Design feature store architectures solving training-serving skew by maintaining identical feature logic for offline training and online inference
- Implement production feature stores using Feast or Tecton with online serving (Redis/DynamoDB, <10ms latency) and offline serving (S3/BigQuery, batch)
- Architect feature engineering pipelines with point-in-time correct joins preventing data leakage and maintaining temporal consistency for model training
- Configure feature materialization strategies including streaming features (Kafka/Flink), batch features (Spark), and on-demand features (real-time computation)
- Design feature reusability patterns enabling feature sharing across teams, models, and use cases reducing engineering duplication by 60-80%
- Implement feature governance including feature documentation, lineage tracking, access control, and deprecated feature management
- Optimize feature serving performance using feature caching, pre-computation, feature sampling, and batch prediction optimization techniques
- Build feature monitoring systems tracking feature drift, staleness, null rates, and distribution shifts to ensure feature quality in production

## Overview

Feature stores solve one of the most critical challenges in production ML: managing, sharing, and serving features consistently across training and inference.

## The Feature Store Problem

### Challenges Without a Feature Store

**Problem 1: Training-Serving Skew**
```python
# Training code (Python, offline)
def calculate_user_features_training(user_data):
    """Calculate features for training"""
    return {
        'avg_purchase_30d': user_data['purchases'].last('30D').mean(),
        'days_since_signup': (datetime.now() - user_data['signup_date']).days,
        'purchase_frequency': len(user_data['purchases']) / max(user_data['days_active'], 1)
    }

# Serving code (different language, online)
// Java serving code - Different logic!
public Map<String, Double> calculateUserFeatures(UserData userData) {
    // Different implementation = training-serving skew
    double avgPurchase = userData.getPurchases()
        .stream()
        .filter(p -> p.isWithinDays(30))
        .mapToDouble(Purchase::getAmount)
        .average()
        .orElse(0.0);
    // ... logic differs slightly, causing skew
}
```

**Problem 2: Feature Recomputation**
```python
# Team A computes features
class RecommendationModel:
    def prepare_features(self, user_id):
        # Complex feature computation
        user_features = compute_user_activity_features(user_id)
        item_features = compute_item_features()
        return combine_features(user_features, item_features)

# Team B computes THE SAME features differently
class FraudDetectionModel:
    def prepare_features(self, user_id):
        # Duplicated computation, possibly inconsistent
        user_features = calculate_user_metrics(user_id)
        # Different implementation for same logical features
        return user_features
```

**Problem 3: Point-in-Time Correctness**
```python
# Incorrect: Using future data in training
def create_training_data():
    """BAD: Data leakage issue"""
    for timestamp in training_timestamps:
        # This gets features as of NOW, not as of timestamp
        features = get_current_features(user_id)  # WRONG!
        label = get_label(user_id, timestamp)
        # Model sees future information it wouldn't have had
```

---

## Feature Store Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Feature Store Architecture                   │
└────────────────────────────────────────────────────────────────┘

        ┌──────────────┐         ┌──────────────┐
        │   Batch      │         │  Streaming   │
        │   Sources    │         │   Sources    │
        └──────┬───────┘         └──────┬───────┘
               │                        │
               └────────┬───────────────┘
                        ▼
              ┌──────────────────┐
              │  Feature Pipeline │
              │  (Computation)    │
              └──────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  Offline Store   │        │   Online Store   │
│  (BigQuery, S3)  │        │  (Redis, DynamoDB)│
└──────────────────┘        └──────────────────┘
          │                           │
          ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  Model Training  │        │  Model Serving   │
│  (Historical)    │        │  (Real-time)     │
└──────────────────┘        └──────────────────┘
```

### Core Components

1. **Feature Registry**: Metadata about features
2. **Offline Store**: Historical features for training
3. **Online Store**: Low-latency feature retrieval
4. **Feature Pipeline**: Computation and ingestion
5. **SDK**: API for accessing features

---

## Implementing a Feature Store with Feast

### Installation and Setup

```bash
# Install Feast
pip install feast[redis,gcs]

# Initialize Feast project
feast init my_feature_repo
cd my_feature_repo
```

### Feature Definitions

```python
# feature_repo/features.py
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

# Define entities (primary keys)
user = Entity(
    name="user_id",
    description="User identifier",
    join_keys=["user_id"]
)

driver = Entity(
    name="driver_id",
    description="Driver identifier",
    join_keys=["driver_id"]
)

# Define data source
user_stats_source = FileSource(
    name="user_stats_source",
    path="/data/user_stats.parquet",
    timestamp_field="event_timestamp"
)

# Define feature view
user_stats_fv = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="trip_count_30d", dtype=Int64),
        Field(name="avg_trip_distance_30d", dtype=Float32),
        Field(name="total_spend_30d", dtype=Float32),
        Field(name="cancellation_rate_30d", dtype=Float32),
        Field(name="avg_rating", dtype=Float32),
    ],
    source=user_stats_source,
    online=True,
    tags={"team": "ml_platform"}
)

driver_stats_source = FileSource(
    name="driver_stats_source",
    path="/data/driver_stats.parquet",
    timestamp_field="event_timestamp"
)

driver_stats_fv = FeatureView(
    name="driver_stats",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="completed_trips_30d", dtype=Int64),
        Field(name="acceptance_rate_30d", dtype=Float32),
        Field(name="avg_customer_rating", dtype=Float32),
        Field(name="earnings_30d", dtype=Float32),
        Field(name="online_hours_30d", dtype=Float32),
    ],
    source=driver_stats_source,
    online=True,
    tags={"team": "driver_ops"}
)
```

### Feature Computation Pipeline

```python
# pipelines/compute_user_features.py
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UserFeatureComputation:
    def __init__(self, trips_data_path):
        self.trips_data_path = trips_data_path

    def load_trips_data(self):
        """Load raw trips data"""
        return pd.read_parquet(self.trips_data_path)

    def compute_features(self, end_date=None):
        """Compute user features for the last 30 days"""
        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=30)

        trips = self.load_trips_data()
        trips['timestamp'] = pd.to_datetime(trips['timestamp'])

        # Filter to time window
        trips_window = trips[
            (trips['timestamp'] >= start_date) &
            (trips['timestamp'] <= end_date)
        ]

        # Aggregate features by user
        user_features = trips_window.groupby('user_id').agg({
            'trip_id': 'count',  # trip_count_30d
            'distance': 'mean',   # avg_trip_distance_30d
            'fare': 'sum',        # total_spend_30d
            'rating': 'mean'      # avg_rating
        }).reset_index()

        user_features.columns = [
            'user_id',
            'trip_count_30d',
            'avg_trip_distance_30d',
            'total_spend_30d',
            'avg_rating'
        ]

        # Calculate cancellation rate
        cancellations = trips_window[trips_window['status'] == 'cancelled']
        cancellation_counts = cancellations.groupby('user_id').size()

        user_features['cancellation_rate_30d'] = (
            cancellation_counts / user_features['trip_count_30d']
        ).fillna(0)

        # Add timestamp
        user_features['event_timestamp'] = end_date

        return user_features

    def save_to_offline_store(self, features, output_path):
        """Save features to offline store"""
        features.to_parquet(output_path, index=False)
        logger.info(f"Saved {len(features)} user features to {output_path}")

# Airflow DAG for feature computation
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def compute_and_materialize_features(**context):
    """Compute features and materialize to Feast"""
    # Compute features
    computer = UserFeatureComputation('/data/trips.parquet')
    features = computer.compute_features()

    # Save to offline store
    computer.save_to_offline_store(features, '/data/user_stats.parquet')

    # Materialize to online store
    from feast import FeatureStore
    store = FeatureStore(repo_path="/feast_repo")
    store.materialize_incremental(end_date=datetime.now())

dag = DAG(
    'compute_user_features',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@hourly',
    catchup=False
)

compute_task = PythonOperator(
    task_id='compute_features',
    python_callable=compute_and_materialize_features,
    dag=dag
)
```

### Using Features in Training

```python
# training/train_model.py
from feast import FeatureStore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def train_model():
    """Train model using Feast features"""
    # Initialize Feast store
    store = FeatureStore(repo_path="/feast_repo")

    # Load training data (entity IDs and labels)
    training_data = pd.read_parquet('/data/training_labels.parquet')
    # Columns: user_id, driver_id, timestamp, label (will_complete)

    # Define features to retrieve
    features = [
        "user_stats:trip_count_30d",
        "user_stats:avg_trip_distance_30d",
        "user_stats:total_spend_30d",
        "user_stats:cancellation_rate_30d",
        "user_stats:avg_rating",
        "driver_stats:completed_trips_30d",
        "driver_stats:acceptance_rate_30d",
        "driver_stats:avg_customer_rating",
        "driver_stats:earnings_30d",
        "driver_stats:online_hours_30d",
    ]

    # Get historical features (point-in-time correct)
    training_features = store.get_historical_features(
        entity_df=training_data,
        features=features
    ).to_df()

    # Training features now have point-in-time correct values
    print(f"Retrieved {len(training_features)} training examples")
    print(f"Features: {training_features.columns.tolist()}")

    # Prepare X and y
    feature_cols = [f for f in training_features.columns
                    if f not in ['user_id', 'driver_id', 'timestamp', 'label']]

    X = training_features[feature_cols]
    y = training_features['label']

    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    print(f"Model accuracy: {model.score(X_test, y_test):.3f}")

    return model

if __name__ == '__main__':
    model = train_model()
```

### Using Features in Serving

```python
# serving/predict_service.py
from feast import FeatureStore
from flask import Flask, request, jsonify
import joblib
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize Feast and load model
store = FeatureStore(repo_path="/feast_repo")
model = joblib.load('models/trip_completion_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    """Real-time prediction endpoint"""
    try:
        # Get request data
        data = request.get_json()
        user_id = data['user_id']
        driver_id = data['driver_id']

        # Define entity rows
        entity_rows = [{
            'user_id': user_id,
            'driver_id': driver_id
        }]

        # Get online features (low latency)
        features = [
            "user_stats:trip_count_30d",
            "user_stats:avg_trip_distance_30d",
            "user_stats:total_spend_30d",
            "user_stats:cancellation_rate_30d",
            "user_stats:avg_rating",
            "driver_stats:completed_trips_30d",
            "driver_stats:acceptance_rate_30d",
            "driver_stats:avg_customer_rating",
            "driver_stats:earnings_30d",
            "driver_stats:online_hours_30d",
        ]

        # Retrieve from online store (Redis)
        online_features = store.get_online_features(
            features=features,
            entity_rows=entity_rows
        ).to_dict()

        # Extract feature values
        feature_values = []
        for feature in features:
            feature_name = feature.split(':')[1]
            feature_values.append(online_features[feature_name][0])

        # Make prediction
        prediction = model.predict([feature_values])[0]
        probability = model.predict_proba([feature_values])[0][1]

        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'user_id': user_id,
            'driver_id': driver_id
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Feature Store Deployment

### Feast Configuration

```yaml
# feature_store.yaml
project: ride_sharing_ml
registry: gs://my-bucket/feast/registry.db
provider: gcp

online_store:
  type: redis
  connection_string: "redis://localhost:6379"

offline_store:
  type: bigquery
  dataset: feast_offline_store
  project_id: my-gcp-project

entity_key_serialization_version: 2
```

### Kubernetes Deployment

```yaml
# k8s/feast-online-serving.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feast-online-serving
spec:
  replicas: 3
  selector:
    matchLabels:
      app: feast-online-serving
  template:
    metadata:
      labels:
        app: feast-online-serving
    spec:
      containers:
      - name: feast-serving
        image: feast/feast-serving:latest
        ports:
        - containerPort: 6566
        env:
        - name: FEAST_CORE_URL
          value: "feast-core:6565"
        - name: FEAST_REDIS_HOST
          value: "redis-master"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: feast-online-serving
spec:
  selector:
    app: feast-online-serving
  ports:
  - port: 6566
    targetPort: 6566
  type: LoadBalancer
```

---

## Advanced Feature Store Patterns

### Real-Time Features with Streaming

```python
# streaming/kafka_feature_processor.py
from kafka import KafkaConsumer
from feast import FeatureStore
import json
import logging

logger = logging.getLogger(__name__)

class RealTimeFeatureProcessor:
    def __init__(self, feast_repo, kafka_bootstrap, topic):
        self.store = FeatureStore(repo_path=feast_repo)
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_bootstrap,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def process_events(self):
        """Process real-time events and update features"""
        for message in self.consumer:
            event = message.value

            try:
                # Extract features from event
                features = self.compute_realtime_features(event)

                # Push to online store
                self.store.push(
                    push_source_name="user_events_push",
                    df=features
                )

                logger.info(f"Processed event for user {event['user_id']}")

            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")

    def compute_realtime_features(self, event):
        """Compute features from real-time event"""
        import pandas as pd

        # Example: compute features from event
        features = pd.DataFrame([{
            'user_id': event['user_id'],
            'event_timestamp': event['timestamp'],
            'last_action': event['action_type'],
            'session_length': event['session_duration'],
            # ... more real-time features
        }])

        return features

# Run processor
if __name__ == '__main__':
    processor = RealTimeFeatureProcessor(
        feast_repo="/feast_repo",
        kafka_bootstrap="localhost:9092",
        topic="user_events"
    )
    processor.process_events()
```

### Feature Transformations

```python
# features/transformations.py
from feast import Field, FeatureView, RequestSource
from feast.types import Float32, Int64
from feast.on_demand_feature_view import on_demand_feature_view
import pandas as pd

# Define request data source
request_source = RequestSource(
    name="trip_request",
    schema=[
        Field(name="pickup_lat", dtype=Float32),
        Field(name="pickup_lon", dtype=Float32),
        Field(name="dropoff_lat", dtype=Float32),
        Field(name="dropoff_lon", dtype=Float32),
    ]
)

@on_demand_feature_view(
    sources=[
        request_source,
        user_stats_fv,  # Reference existing feature view
    ],
    schema=[
        Field(name="trip_distance_estimate", dtype=Float32),
        Field(name="trip_distance_ratio", dtype=Float32),
        Field(name="user_affordability_score", dtype=Float32),
    ]
)
def trip_features(inputs: pd.DataFrame) -> pd.DataFrame:
    """Compute on-demand features from request and stored features"""
    import numpy as np

    # Calculate estimated trip distance
    df = pd.DataFrame()
    df['trip_distance_estimate'] = np.sqrt(
        (inputs['dropoff_lat'] - inputs['pickup_lat']) ** 2 +
        (inputs['dropoff_lon'] - inputs['pickup_lon']) ** 2
    ) * 111  # Convert to km

    # Ratio compared to user's average
    df['trip_distance_ratio'] = (
        df['trip_distance_estimate'] / inputs['avg_trip_distance_30d']
    ).fillna(1.0)

    # Affordability score based on spending patterns
    estimated_fare = df['trip_distance_estimate'] * 2.5  # $2.5 per km
    df['user_affordability_score'] = (
        inputs['total_spend_30d'] / (estimated_fare * 30)
    ).clip(0, 1)

    return df
```

---

## Feature Store Comparison

### Feast vs Tecton vs AWS Feature Store

| Feature | Feast | Tecton | AWS Feature Store |
|---------|-------|--------|-------------------|
| Open Source | Yes | No | No |
| Online Store | Redis, DynamoDB | Proprietary | DynamoDB |
| Offline Store | BigQuery, Snowflake, S3 | S3, Snowflake | S3 |
| Streaming | Kafka, Kinesis | Native | Kinesis |
| Feature Transformations | Python | Pyspark, SQL | Spark |
| Cost | Free (infra costs) | $$$$ | $$$ |
| Vendor Lock-in | Low | High | Medium |

---

## Feature Governance

### Feature Documentation

```python
# features/documented_features.py
from feast import FeatureView, Field
from feast.types import Float32, Int64

user_financial_features = FeatureView(
    name="user_financial_features",
    entities=[user],
    schema=[
        Field(
            name="credit_score",
            dtype=Int64,
            description="User's credit score from credit bureau",
            tags={
                "pii": "false",
                "owner": "risk_team",
                "sla": "daily",
                "data_source": "credit_bureau_api"
            }
        ),
        Field(
            name="total_spend_30d",
            dtype=Float32,
            description="Total spending in last 30 days",
            tags={
                "pii": "false",
                "owner": "analytics_team",
                "sla": "hourly",
                "data_source": "transactions_db"
            }
        ),
    ],
    source=financial_data_source,
    ttl=timedelta(days=1),
    online=True,
    tags={
        "team": "ml_platform",
        "access_level": "confidential",
        "compliance": "gdpr_compliant"
    }
)
```

### Feature Monitoring

```python
# monitoring/feature_monitor.py
from feast import FeatureStore
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class FeatureMonitor:
    def __init__(self, feast_repo):
        self.store = FeatureStore(repo_path=feast_repo)

    def check_data_drift(self, feature_view_name, reference_data, current_data):
        """Check for data drift in features"""
        drift_results = {}

        for column in reference_data.columns:
            if column in ['user_id', 'timestamp']:
                continue

            # Kolmogorov-Smirnov test
            statistic, pvalue = stats.ks_2samp(
                reference_data[column].dropna(),
                current_data[column].dropna()
            )

            drift_detected = pvalue < 0.05
            drift_results[column] = {
                'statistic': statistic,
                'pvalue': pvalue,
                'drift_detected': drift_detected
            }

            if drift_detected:
                logger.warning(
                    f"Data drift detected in {feature_view_name}.{column}: "
                    f"p-value={pvalue:.4f}"
                )

        return drift_results

    def check_feature_freshness(self, feature_view_name):
        """Check if features are fresh"""
        # Query latest feature timestamps
        # Alert if features are stale
        pass

    def monitor_feature_quality(self):
        """Comprehensive feature quality monitoring"""
        # Check for nulls, outliers, drift
        pass

# Usage
monitor = FeatureMonitor("/feast_repo")
```

---

## Best Practices

1. **Feature Naming**: Use consistent naming conventions
   - `{entity}_{aggregation}_{time_window}`
   - Example: `user_avg_purchase_30d`

2. **Feature TTL**: Set appropriate TTL for feature freshness

3. **Point-in-Time Correctness**: Always use historical retrieval for training

4. **Feature Reuse**: Share features across teams through feature registry

5. **Monitoring**: Monitor feature drift and freshness

6. **Documentation**: Document features with tags and descriptions

7. **Access Control**: Implement proper access controls for sensitive features

## Key Takeaways

- Feature stores solve training-serving skew
- Point-in-time correctness prevents data leakage
- Online and offline stores serve different purposes
- Feature reuse improves efficiency
- Governance and monitoring are critical

## Exercises

1. Implement a Feast feature store with both online and offline stores
2. Create a feature computation pipeline with Airflow
3. Build a prediction service that uses online features
4. Implement data drift detection for features
5. Create on-demand feature transformations

## Additional Resources

- Feast documentation: https://docs.feast.dev
- "Feature Store for ML" by Tecton
- "Rethinking Feature Stores" by Eugene Yan
- Feast examples repository
