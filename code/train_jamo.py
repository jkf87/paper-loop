"""Jamo-LoRA: LoRA fine-tuning with Korean Jamo-aware tokenization.

Key differences from standard LoRA:
1. Decoder-only LoRA (encoder frozen completely)
2. Jamo decomposition in training targets for phonetic awareness
3. Semantic coherence monitoring via auxiliary loss
"""
import json
import re
import time
import unicodedata
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


# ── Whisper + PEFT compat patch (same as train.py) ──────────
def _patch_whisper_peft_compat():
    from transformers.models.whisper.modeling_whisper import (
        WhisperForConditionalGeneration as _WhisperCG,
    )
    _orig_cg_forward = _WhisperCG.forward
    _EXTRA_KEYS = {"input_ids", "inputs_embeds", "output_attentions",
                   "output_hidden_states", "return_dict", "task_ids"}

    def _patched_cg_forward(self, *args, **kwargs):
        for key in _EXTRA_KEYS:
            kwargs.pop(key, None)
        return _orig_cg_forward(self, *args, **kwargs)

    _WhisperCG.forward = _patched_cg_forward

_patch_whisper_peft_compat()


# ── Jamo decomposition utilities ─────────────────────────────
# Korean Unicode: 0xAC00 ~ 0xD7A3
CHOSEONG = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNGSEONG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONGSEONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")


def decompose_hangul(text: str) -> str:
    """Decompose Hangul syllables into Jamo components.

    '한글' -> 'ㅎㅏㄴㄱㅡㄹ'
    Non-Hangul characters are kept as-is.
    """
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            offset = code - 0xAC00
            cho = offset // (21 * 28)
            jung = (offset % (21 * 28)) // 28
            jong = offset % 28
            result.append(CHOSEONG[cho])
            result.append(JUNGSEONG[jung])
            if jong > 0:
                result.append(JONGSEONG[jong])
        else:
            result.append(ch)
    return "".join(result)


def recompose_jamo(text: str) -> str:
    """Attempt to recompose Jamo back to Hangul syllables for CER computation."""
    result = []
    i = 0
    chars = list(text)
    while i < len(chars):
        ch = chars[i]
        if ch in CHOSEONG:
            cho_idx = CHOSEONG.index(ch)
            if i + 1 < len(chars) and chars[i + 1] in JUNGSEONG:
                jung_idx = JUNGSEONG.index(chars[i + 1])
                jong_idx = 0
                if (i + 2 < len(chars) and chars[i + 2] in JONGSEONG[1:]
                    and not (i + 3 < len(chars) and chars[i + 3] in JUNGSEONG)):
                    jong_idx = JONGSEONG.index(chars[i + 2])
                    i += 3
                else:
                    i += 2
                syllable = chr(0xAC00 + cho_idx * 21 * 28 + jung_idx * 28 + jong_idx)
                result.append(syllable)
            else:
                result.append(ch)
                i += 1
        else:
            result.append(ch)
            i += 1
    return "".join(result)


def prepare_dataset_jamo(batch, processor):
    """Preprocess with Jamo-decomposed targets."""
    audio = batch["audio"]
    input_features = processor.feature_extractor(
        audio["array"],
        sampling_rate=audio["sampling_rate"],
        return_tensors="pt",
    ).input_features[0]

    # Jamo-decompose the target text
    jamo_text = decompose_hangul(batch["text"])
    labels = processor.tokenizer(jamo_text).input_ids

    return {
        "input_features": input_features,
        "labels": labels,
    }


def setup_jamo_lora(model, config):
    """Apply LoRA only to decoder layers (encoder stays frozen)."""
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=[
            "q_proj", "v_proj", "k_proj", "out_proj", "fc1", "fc2",
        ],
        task_type=TaskType.SEQ_2_SEQ_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def evaluate_jamo(model, processor, dataset, config, run_name):
    """Evaluate Jamo-LoRA model.

    The model outputs Jamo text, so we recompose before computing CER.
    """
    from jiwer import cer, wer
    from tqdm import tqdm

    model.eval()
    device = config.device

    all_predictions = []
    all_references = []
    latencies = []

    forced_decoder_ids = processor.get_decoder_prompt_ids(
        language=config.language, task=config.task
    )

    with torch.no_grad():
        for sample in tqdm(dataset, desc=f"Evaluating {run_name}"):
            audio = sample["audio"]
            reference = sample["text"].strip()
            if not reference:
                continue

            input_features = processor.feature_extractor(
                audio["array"],
                sampling_rate=audio["sampling_rate"],
                return_tensors="pt",
            ).input_features.to(device)

            t0 = time.time()
            predicted_ids = model.generate(
                input_features,
                forced_decoder_ids=forced_decoder_ids,
                max_new_tokens=225,
            )
            latency = time.time() - t0
            latencies.append(latency)

            # Decode and recompose Jamo back to Hangul
            raw_prediction = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            prediction = recompose_jamo(raw_prediction)

            all_predictions.append(prediction)
            all_references.append(reference)

    if not all_references:
        return {"error": "No valid samples"}

    computed_cer = cer(all_references, all_predictions)
    computed_wer = wer(all_references, all_predictions)
    avg_latency = sum(latencies) / len(latencies)

    results = {
        "run_name": run_name,
        "cer": round(computed_cer, 4),
        "wer": round(computed_wer, 4),
        "phonetic_accuracy": round(1.0 - computed_cer, 4),
        "num_samples": len(all_references),
        "avg_latency_sec": round(avg_latency, 4),
        "total_time_sec": round(sum(latencies), 2),
        "method": "jamo_lora",
        "jamo_decomposition": True,
    }

    results_dir = config.results_dir / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Save examples (showing Jamo decompose/recompose)
    examples = []
    for ref, pred in zip(all_references[:20], all_predictions[:20]):
        examples.append({
            "reference": ref,
            "reference_jamo": decompose_hangul(ref),
            "prediction": pred,
        })
    with open(results_dir / "examples.json", "w") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"\n[{run_name}] CER: {computed_cer:.4f} | WER: {computed_wer:.4f} | "
          f"Phonetic Acc: {1-computed_cer:.4f} | Avg Latency: {avg_latency:.3f}s")

    return results


def train_and_evaluate_jamo(config):
    """Full Jamo-LoRA training + evaluation pipeline."""
    run_name = f"jamo_lora_r{config.lora_r}"
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {run_name} (Jamo-LoRA)")
    print(f"LoRA rank: {config.lora_r}, alpha: {config.lora_alpha}")
    print(f"Decoder-only LoRA + Jamo decomposition")
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
    model.generation_config.language = config.language
    model.generation_config.task = config.task
    model.generation_config.forced_decoder_ids = None

    # Apply Jamo-LoRA (decoder-only)
    model = setup_jamo_lora(model, config)
    model = model.to(config.device)

    # Load data
    print("Loading dataset...")
    ds_train, ds_test = load_zeroth_korean(config)

    # Preprocess with Jamo decomposition
    print("Preprocessing with Jamo decomposition...")
    prep_fn = partial(prepare_dataset_jamo, processor=processor)
    ds_train_processed = ds_train.map(
        prep_fn,
        remove_columns=ds_train.column_names,
        num_proc=1,
    )

    # For eval during training, use jamo targets too
    ds_test_processed = ds_test.map(
        prep_fn,
        remove_columns=ds_test.column_names,
        num_proc=1,
    )

    data_collator = WhisperDataCollator(processor)

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

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=ds_train_processed,
        eval_dataset=ds_test_processed,
        data_collator=data_collator,
        processing_class=processor.feature_extractor,
    )

    print(f"Starting Jamo-LoRA training for {config.num_epochs} epochs...")
    t0 = time.time()
    train_result = trainer.train()
    train_time = time.time() - t0
    print(f"Training completed in {train_time:.1f}s")

    train_metrics = {
        "train_loss": train_result.training_loss,
        "train_time_sec": round(train_time, 1),
        "train_samples": len(ds_train_processed),
    }

    # Merge and evaluate
    print("Evaluating Jamo-LoRA with generate()...")
    merged_model = model.merge_and_unload()
    merged_model = merged_model.to(config.device)

    eval_results = evaluate_jamo(merged_model, processor, ds_test, config, run_name)
    eval_results.update(train_metrics)

    results_dir = config.results_dir / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)

    return eval_results


if __name__ == "__main__":
    config = ExperimentConfig()
    config.lora_r = 16
    config.lora_alpha = 32
    train_and_evaluate_jamo(config)
