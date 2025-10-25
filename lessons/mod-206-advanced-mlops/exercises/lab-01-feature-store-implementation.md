# Lab 01: Feature Store Implementation with Feast

## Objective
Implement a production-ready feature store using Feast, including online and offline feature serving for a machine learning model.

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Kubernetes cluster (local or cloud)
- Basic understanding of ML workflows

## Duration
4-6 hours

## Lab Architecture

```
┌──────────────────────────────────────────────────────┐
│         Feature Store Lab Architecture                │
└──────────────────────────────────────────────────────┘

Raw Data Sources          Feature Store              Consumers
┌──────────────┐         ┌─────────────┐           ┌──────────┐
│   Postgres   │────────▶│  Offline    │──────────▶│ Training │
│   (Events)   │         │   Store     │           │ Pipeline │
└──────────────┘         │ (BigQuery)  │           └──────────┘
                         └─────────────┘
┌──────────────┐                │
│    Kafka     │         ┌─────────────┐           ┌──────────┐
│  (Streaming) │────────▶│  Feature    │──────────▶│  Online  │
└──────────────┘         │  Pipeline   │           │ Serving  │
                         └─────────────┘           └──────────┘
┌──────────────┐                │
│   CSV Files  │         ┌─────────────┐
│  (Batch)     │────────▶│   Online    │
└──────────────┘         │   Store     │
                         │  (Redis)    │
                         └─────────────┘
```

## Part 1: Environment Setup (30 min)

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv feast-env
source feast-env/bin/activate  # On Windows: feast-env\Scripts\activate

# Install Feast with Redis and GCS support
pip install 'feast[redis,gcs]'==0.35.0
pip install pandas scikit-learn mlflow
```

### Step 2: Start Infrastructure

```bash
# Create docker-compose.yml for Redis
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
COMPOSE

# Start Redis
docker-compose up -d
```

### Step 3: Initialize Feast Project

```bash
# Initialize Feast repository
feast init feature_repo
cd feature_repo
```

## Part 2: Define Features (45 min)

### Step 1: Create Feature Definitions

Create `feature_repo/features.py`:

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, PushSource, ValueType
from feast.types import Float32, Int64, String, UnixTimestamp

# Define entities
user = Entity(
    name="user_id",
    description="User identifier",
)

driver = Entity(
    name="driver_id",
    description="Driver identifier",
)

# TODO: Define offline data source for user statistics
user_stats_source = FileSource(
    # TODO: Set path to your parquet file
    path="data/user_stats.parquet",
    # TODO: Set timestamp field
    timestamp_field="event_timestamp",
)

# TODO: Define feature view for user statistics
user_stats_fv = FeatureView(
    # TODO: Set name
    # TODO: Set entities
    # TODO: Set TTL
    # TODO: Define schema with Field objects
    # TODO: Set source
    # TODO: Enable online serving
)

# TODO: Define driver statistics feature view
# Include fields:
# - completed_trips_30d (Int64)
# - acceptance_rate_30d (Float32)
# - avg_rating (Float32)
# - earnings_30d (Float32)

# TODO: Define streaming data source
user_activity_push_source = PushSource(
    name="user_activity_push",
    batch_source=user_stats_source,
)

# TODO: Create on-demand feature view for computed features
```

### Step 2: Configure Feature Store

Edit `feature_repo/feature_store.yaml`:

```yaml
# TODO: Set project name
project: ride_sharing_ml
# TODO: Set registry location
registry: data/registry.db
# TODO: Set provider
provider: local

# TODO: Configure online store (Redis)
online_store:
  type: redis
  connection_string: "redis://localhost:6379"

# TODO: Configure offline store
offline_store:
  type: file
```

## Part 3: Generate Sample Data (30 min)

Create `generate_data.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_user_stats(n_users=1000, n_days=30):
    """Generate sample user statistics"""
    # TODO: Generate user IDs
    user_ids = [f"user_{i}" for i in range(n_users)]

    data = []
    end_date = datetime.now()

    for days_ago in range(n_days):
        timestamp = end_date - timedelta(days=days_ago)

        for user_id in user_ids:
            # TODO: Generate realistic features
            # - trip_count_30d
            # - avg_trip_distance_30d
            # - total_spend_30d
            # - cancellation_rate_30d
            # - avg_rating

            # Example:
            row = {
                'user_id': user_id,
                'event_timestamp': timestamp,
                'trip_count_30d': np.random.randint(0, 50),
                # TODO: Add more features
            }
            data.append(row)

    df = pd.DataFrame(data)
    return df

def generate_driver_stats(n_drivers=500, n_days=30):
    """Generate sample driver statistics"""
    # TODO: Implement driver statistics generation
    pass

if __name__ == '__main__':
    # Generate and save data
    user_stats = generate_user_stats()
    user_stats.to_parquet('data/user_stats.parquet', index=False)
    print(f"Generated {len(user_stats)} user stat records")

    # TODO: Generate driver stats
    # driver_stats = generate_driver_stats()
    # driver_stats.to_parquet('data/driver_stats.parquet', index=False)
```

Run the data generation:
```bash
mkdir -p data
python generate_data.py
```

## Part 4: Apply Feature Definitions (15 min)

```bash
# Apply feature definitions to registry
feast apply

# Verify features are registered
feast feature-views list
feast entities list
```

## Part 5: Materialize Features to Online Store (30 min)

Create `materialize_features.py`:

```python
from feast import FeatureStore
from datetime import datetime, timedelta

# TODO: Initialize feature store
store = FeatureStore(repo_path=".")

# TODO: Materialize features to online store
# Use store.materialize() or store.materialize_incremental()

# Example:
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

print(f"Materializing features from {start_date} to {end_date}")

# TODO: Call materialize method
# store.materialize(start_date=start_date, end_date=end_date)

print("Materialization complete")
```

Run materialization:
```bash
python materialize_features.py
```

## Part 6: Training with Historical Features (45 min)

Create `train_model.py`:

```python
from feast import FeatureStore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import mlflow

def train_model():
    # TODO: Initialize Feast store
    store = FeatureStore(repo_path=".")

    # TODO: Create entity DataFrame with timestamps
    # This represents your training labels
    entity_df = pd.DataFrame({
        'user_id': ['user_1', 'user_2', 'user_3', ...],
        'driver_id': ['driver_1', 'driver_2', 'driver_3', ...],
        'event_timestamp': [...],  # Historical timestamps
        'trip_completed': [1, 0, 1, ...]  # Label
    })

    # TODO: Define features to retrieve
    features = [
        "user_stats:trip_count_30d",
        "user_stats:avg_trip_distance_30d",
        # TODO: Add more features
    ]

    # TODO: Get historical features (point-in-time correct)
    # training_df = store.get_historical_features(
    #     entity_df=entity_df,
    #     features=features
    # ).to_df()

    # TODO: Prepare X and y
    # feature_cols = [col for col in training_df.columns
    #                 if col not in ['user_id', 'driver_id', 'event_timestamp', 'trip_completed']]
    # X = training_df[feature_cols]
    # y = training_df['trip_completed']

    # TODO: Split data
    # X_train, X_test, y_train, y_test = train_test_split(...)

    # TODO: Train model
    # model = RandomForestClassifier()
    # model.fit(X_train, y_train)

    # TODO: Evaluate
    # predictions = model.predict(X_test)
    # accuracy = accuracy_score(y_test, predictions)
    # print(f"Model accuracy: {accuracy:.3f}")

    # TODO: Log with MLflow
    # with mlflow.start_run():
    #     mlflow.log_metric("accuracy", accuracy)
    #     mlflow.sklearn.log_model(model, "model")

    return model

if __name__ == '__main__':
    model = train_model()
```

## Part 7: Online Serving (45 min)

Create `serving.py`:

```python
from flask import Flask, request, jsonify
from feast import FeatureStore
import joblib
import numpy as np

app = Flask(__name__)

# TODO: Initialize Feast store
store = FeatureStore(repo_path=".")

# TODO: Load trained model
model = joblib.load('models/model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    """Real-time prediction endpoint"""
    try:
        data = request.get_json()

        # TODO: Extract entity IDs
        user_id = data['user_id']
        driver_id = data['driver_id']

        # TODO: Create entity rows for online retrieval
        entity_rows = [{
            'user_id': user_id,
            'driver_id': driver_id
        }]

        # TODO: Define features to retrieve
        features = [
            "user_stats:trip_count_30d",
            "user_stats:avg_trip_distance_30d",
            # Add all features used in training
        ]

        # TODO: Get online features (low latency from Redis)
        # online_features = store.get_online_features(
        #     features=features,
        #     entity_rows=entity_rows
        # ).to_dict()

        # TODO: Extract feature values in correct order
        # feature_values = [...]

        # TODO: Make prediction
        # prediction = model.predict([feature_values])[0]
        # probability = model.predict_proba([feature_values])[0][1]

        return jsonify({
            # TODO: Return prediction results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Part 8: Streaming Features (Bonus - 60 min)

Create `stream_processor.py`:

```python
from feast import FeatureStore
import pandas as pd
from kafka import KafkaConsumer
import json

# TODO: Initialize Feast store
store = FeatureStore(repo_path=".")

# TODO: Set up Kafka consumer
consumer = KafkaConsumer(
    'user_events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def process_event(event):
    """Process streaming event and update features"""
    # TODO: Extract features from event

    # TODO: Create DataFrame
    df = pd.DataFrame([{
        'user_id': event['user_id'],
        'event_timestamp': pd.to_datetime(event['timestamp']),
        # ... features computed from event
    }])

    # TODO: Push to online store
    # store.push('user_activity_push', df)

for message in consumer:
    event = message.value
    process_event(event)
```

## Deliverables

1. **Feature Definitions** (`features.py`)
   - At least 2 feature views with 5+ features each
   - Proper entity definitions
   - Correctly configured sources

2. **Data Generation** (`generate_data.py`)
   - Generates realistic training data
   - Proper timestamps for point-in-time correctness

3. **Training Script** (`train_model.py`)
   - Uses historical features from Feast
   - Achieves >80% accuracy
   - Logs results to MLflow

4. **Serving Endpoint** (`serving.py`)
   - Retrieves online features
   - Low-latency predictions (<100ms)
   - Proper error handling

5. **Documentation**
   - README explaining architecture
   - Instructions for running the system
   - Performance benchmarks

## Validation Criteria

- [ ] Features properly registered in Feast
- [ ] Online store (Redis) contains materialized features
- [ ] Training retrieves historical features correctly
- [ ] Serving endpoint responds in <100ms
- [ ] Model achieves >80% accuracy
- [ ] Point-in-time correctness verified
- [ ] Streaming ingestion working (bonus)

## Common Issues and Solutions

**Issue**: Features not found in online store
- **Solution**: Run `feast materialize` to populate online store

**Issue**: Training-serving skew
- **Solution**: Use same feature retrieval logic for training and serving

**Issue**: Timestamp errors
- **Solution**: Ensure all timestamps are timezone-aware

## Extensions

1. **Add Feature Monitoring**: Track feature drift over time
2. **Implement Feature Versioning**: Support multiple feature versions
3. **Add Feature Validation**: Validate feature quality before materialization
4. **Create Feature Dashboard**: Visualize feature statistics
5. **Implement Feature Backfilling**: Backfill historical features efficiently

## Resources

- Feast documentation: https://docs.feast.dev
- Feast examples: https://github.com/feast-dev/feast/tree/master/examples
- Feature store patterns: https://www.featurestore.org
