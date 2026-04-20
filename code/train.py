"""Training: LoRA fine-tuning of Whisper for Korean ASR."""
import json
import time
from functools import partial
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model, TaskType
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from config import ExperimentConfig
from data import load_zeroth_korean, prepare_dataset, WhisperDataCollator
from evaluate_model import evaluate_whisper


def _patch_whisper_peft_compat():
    """Fix PEFT + Whisper incompatibility in transformers>=5 + peft>=0.18.

    Bug: PEFT's PeftModelForSeq2SeqLM.forward passes input_ids, inputs_embeds,
    decoder_inputs_embeds, etc. as explicit kwargs to LoraModel, which passes them
    through to WhisperForConditionalGeneration -> WhisperModel -> WhisperDecoder.
    Both WhisperForConditionalGeneration and WhisperModel use **kwargs pass-through,
    which causes duplicate keyword arguments at the decoder level.

    Fix: Patch WhisperForConditionalGeneration.forward to strip PEFT-injected kwargs
    that are not part of its expected signature before they leak into sub-models.
    """
    from transformers.models.whisper.modeling_whisper import (
        WhisperForConditionalGeneration as _WhisperCG,
    )

    _orig_cg_forward = _WhisperCG.forward

    # These keys come from PEFT but are not in WhisperForConditionalGeneration's
    # explicit forward() signature, so they end up in **kwargs and leak through.
    _EXTRA_KEYS = {"input_ids", "inputs_embeds", "output_attentions",
                   "output_hidden_states", "return_dict", "task_ids"}

    def _patched_cg_forward(self, *args, **kwargs):
        for key in _EXTRA_KEYS:
            kwargs.pop(key, None)
        return _orig_cg_forward(self, *args, **kwargs)

    _WhisperCG.forward = _patched_cg_forward


_patch_whisper_peft_compat()


def setup_lora_model(model, config):
    """Apply LoRA adapters to Whisper model."""
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.lora_target_modules,
        task_type=TaskType.SEQ_2_SEQ_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def train_and_evaluate(config, experiment_type="standard_lora"):
    """Full training + evaluation pipeline."""
    run_name = config.run_name(experiment_type)
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {run_name}")
    print(f"LoRA rank: {config.lora_r}, alpha: {config.lora_alpha}")
    print(f"{'='*60}\n")

    # Load model and processor
    processor = WhisperProcessor.from_pretrained(
        config.model_name,
        cache_dir=str(config.data_cache),
    )
    model = WhisperForConditionalGeneration.from_pretrained(
        config.model_name,
        cache_dir=str(config.data_cache),
    )

    # Force Korean language for generation
    model.generation_config.language = config.language
    model.generation_config.task = config.task
    model.generation_config.forced_decoder_ids = None

    # Apply LoRA
    model = setup_lora_model(model, config)
    model = model.to(config.device)

    # Load data
    print("Loading dataset...")
    ds_train, ds_test = load_zeroth_korean(config)

    # Preprocess
    print("Preprocessing...")
    prep_fn = partial(prepare_dataset, processor=processor)
    ds_train_processed = ds_train.map(
        prep_fn,
        remove_columns=ds_train.column_names,
        num_proc=1,
    )
    ds_test_processed = ds_test.map(
        prep_fn,
        remove_columns=ds_test.column_names,
        num_proc=1,
    )

    # Data collator
    data_collator = WhisperDataCollator(processor)

    # Training arguments
    output_dir = str(config.checkpoint_dir / run_name)
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        num_train_epochs=config.num_epochs,
        fp16=False,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=25,
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        seed=config.seed,
        remove_unused_columns=False,
        label_names=["labels"],
        report_to="none",
        dataloader_num_workers=0,
    )

    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=ds_train_processed,
        eval_dataset=ds_test_processed,
        data_collator=data_collator,
        processing_class=processor.feature_extractor,
    )

    # Train
    print(f"Starting training for {config.num_epochs} epochs...")
    t0 = time.time()
    train_result = trainer.train()
    train_time = time.time() - t0
    print(f"Training completed in {train_time:.1f}s")

    # Save training metrics
    train_metrics = {
        "train_loss": train_result.training_loss,
        "train_time_sec": round(train_time, 1),
        "train_samples": len(ds_train_processed),
    }

    # Evaluate using generate (not just loss)
    print("Evaluating with generate()...")
    # Merge LoRA for faster inference
    merged_model = model.merge_and_unload()
    merged_model = merged_model.to(config.device)

    eval_results = evaluate_whisper(merged_model, processor, ds_test, config, run_name)
    eval_results.update(train_metrics)

    # Save combined results
    results_dir = config.results_dir / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)

    return eval_results


if __name__ == "__main__":
    import sys
    config = ExperimentConfig()

    if len(sys.argv) > 1:
        config.lora_r = int(sys.argv[1])
        config.lora_alpha = config.lora_r * 2

    train_and_evaluate(config, experiment_type="standard_lora")
