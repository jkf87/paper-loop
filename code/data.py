"""Data loading and preprocessing for Korean ASR experiments."""
import torch
from datasets import load_dataset, Audio
from transformers import WhisperProcessor


def load_zeroth_korean(config):
    """Load zeroth_korean dataset with audio resampled to 16kHz."""
    ds_train = load_dataset(
        config.dataset_name,
        split="train",
        cache_dir=str(config.data_cache),
    )
    ds_test = load_dataset(
        config.dataset_name,
        split="test",
        cache_dir=str(config.data_cache),
    )

    # Subsample training set if needed
    if config.max_train_samples and len(ds_train) > config.max_train_samples:
        ds_train = ds_train.shuffle(seed=config.seed).select(range(config.max_train_samples))

    if config.max_eval_samples and len(ds_test) > config.max_eval_samples:
        ds_test = ds_test.shuffle(seed=config.seed).select(range(config.max_eval_samples))

    # Resample audio to 16kHz (Whisper requirement)
    ds_train = ds_train.cast_column("audio", Audio(sampling_rate=16000))
    ds_test = ds_test.cast_column("audio", Audio(sampling_rate=16000))

    return ds_train, ds_test


def prepare_dataset(batch, processor):
    """Preprocess a batch for Whisper training."""
    audio = batch["audio"]
    input_features = processor.feature_extractor(
        audio["array"],
        sampling_rate=audio["sampling_rate"],
        return_tensors="pt",
    ).input_features[0]

    # Encode target text
    labels = processor.tokenizer(batch["text"]).input_ids

    return {
        "input_features": input_features,
        "labels": labels,
    }


class WhisperDataCollator:
    """Custom data collator for Whisper that pads labels."""

    def __init__(self, processor):
        self.processor = processor

    def __call__(self, features):
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # Replace padding token id's of the labels by -100
        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )

        # Cut bos token if present
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch
