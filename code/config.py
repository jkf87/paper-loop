"""Experiment configuration for Jamo-LoRA."""
from dataclasses import dataclass, field
from pathlib import Path

SSD_BASE = Path("/Volumes/Samsung_T5/jamo-lora")
PROJECT_BASE = Path("/Users/conanssam-m4/autoresearch-paper/jamo-lora")

@dataclass
class ExperimentConfig:
    # Paths
    data_cache: Path = SSD_BASE / "hf-cache"
    checkpoint_dir: Path = SSD_BASE / "checkpoints"
    results_dir: Path = PROJECT_BASE / "results"
    figures_dir: Path = PROJECT_BASE / "figures"

    # Model
    model_name: str = "openai/whisper-small"
    language: str = "ko"
    task: str = "transcribe"

    # Dataset
    dataset_name: str = "kresnik/zeroth_korean"
    max_train_samples: int = 1000   # ~1h subset for fast iteration
    max_eval_samples: int = 457     # full test set

    # Training
    num_epochs: int = 1
    batch_size: int = 4
    gradient_accumulation_steps: int = 4  # effective batch 16
    learning_rate: float = 3e-4
    warmup_steps: int = 20
    fp16: bool = False  # MPS doesn't support fp16 training well
    seed: int = 42

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    lora_target_modules: list = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "out_proj",
        "fc1", "fc2",
    ])

    # Device
    device: str = "mps"  # Apple M4

    def run_name(self, experiment_type: str = "baseline") -> str:
        if experiment_type == "baseline":
            return "baseline_whisper_small"
        elif experiment_type == "standard_lora":
            return f"standard_lora_r{self.lora_r}"
        else:
            return f"jamo_lora_r{self.lora_r}"
