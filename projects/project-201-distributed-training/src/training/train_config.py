"""Training configuration dataclass and utilities."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml


@dataclass
class TrainingConfig:
    """
    Configuration for distributed training.

    TODO: Add any additional fields needed for your specific use case.
    Consider adding:
    - Data augmentation parameters
    - Advanced optimizer settings
    - Custom callback configurations
    - Logging preferences
    """

    # Model configuration
    model_name: str = "resnet50"
    num_classes: int = 1000
    pretrained: bool = False

    # Dataset configuration
    dataset: str = "imagenet"
    data_dir: str = "/mnt/data"
    num_dataloader_workers: int = 4
    prefetch_factor: int = 2

    # Training hyperparameters
    num_epochs: int = 100
    batch_size: int = 128
    learning_rate: float = 0.001
    weight_decay: float = 1e-4
    momentum: float = 0.9

    # Optimizer configuration
    optimizer: str = "sgd"  # sgd, adam, adamw
    scheduler: str = "cosine"  # cosine, step, exponential
    warmup_epochs: int = 5
    warmup_lr: float = 1e-6

    # Distributed configuration
    num_workers: int = 4
    gpus_per_worker: int = 2
    backend: str = "nccl"

    # Mixed precision training
    use_amp: bool = True
    amp_dtype: str = "float16"  # float16 or bfloat16

    # Gradient configuration
    gradient_accumulation_steps: int = 1
    gradient_clipping_norm: float = 1.0
    enable_gradient_checkpointing: bool = False

    # Checkpoint configuration
    checkpoint_dir: str = "/mnt/checkpoints"
    checkpoint_frequency: int = 5  # Save every N epochs
    checkpoint_keep_n: int = 5  # Keep last N checkpoints
    resume_from_checkpoint: Optional[str] = None

    # Metrics and logging
    mlflow_tracking_uri: str = "http://mlflow:5000"
    mlflow_experiment_name: str = "distributed-training"
    log_frequency: int = 10  # Log every N steps

    # Performance optimization
    enable_profiling: bool = False
    profile_steps: List[int] = field(default_factory=lambda: [100, 200])
    num_workers_dataloader: int = 4

    # Early stopping
    enable_early_stopping: bool = True
    early_stopping_patience: int = 10
    early_stopping_metric: str = "val/loss"
    early_stopping_mode: str = "min"  # min or max

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "TrainingConfig":
        """
        Load configuration from YAML file.

        TODO: Implement YAML configuration loading.
        1. Read the YAML file
        2. Parse the configuration
        3. Validate required fields
        4. Handle defaults for missing fields
        5. Return TrainingConfig instance

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            TrainingConfig instance
        """
        # TODO: Implement YAML loading
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TrainingConfig":
        """
        Create configuration from dictionary.

        TODO: Implement dictionary-based configuration.
        1. Extract relevant fields from dictionary
        2. Handle nested configurations
        3. Apply validation
        4. Return TrainingConfig instance

        Args:
            config_dict: Configuration dictionary

        Returns:
            TrainingConfig instance
        """
        # TODO: Implement dictionary parsing
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        TODO: Implement configuration serialization.
        1. Convert all fields to dictionary
        2. Handle special types (Path, etc.)
        3. Return serializable dictionary

        Returns:
            Configuration dictionary
        """
        # TODO: Implement dictionary conversion
        return self.__dict__.copy()

    def validate(self) -> None:
        """
        Validate configuration parameters.

        TODO: Implement comprehensive validation:
        1. Check that all required fields are set
        2. Validate value ranges (e.g., learning_rate > 0)
        3. Validate file paths exist if resuming from checkpoint
        4. Validate compatibility between options
        5. Raise ValueError for invalid configurations

        Raises:
            ValueError: If configuration is invalid
        """
        # TODO: Implement validation logic
        if self.num_epochs <= 0:
            raise ValueError("num_epochs must be positive")

        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")

        # TODO: Add more validation checks
        pass

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
