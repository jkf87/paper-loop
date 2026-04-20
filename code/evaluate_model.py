"""Evaluation: compute CER/WER on test set."""
import json
import time
from pathlib import Path

import torch
from jiwer import cer, wer
from tqdm import tqdm
from transformers import WhisperForConditionalGeneration, WhisperProcessor


def evaluate_whisper(model, processor, dataset, config, run_name="baseline"):
    """Evaluate a Whisper model on the test set.

    Returns dict with CER, WER, latency stats.
    """
    model.eval()
    device = config.device

    all_predictions = []
    all_references = []
    latencies = []

    forced_decoder_ids = processor.get_decoder_prompt_ids(
        language=config.language, task=config.task
    )

    with torch.no_grad():
        for i, sample in enumerate(tqdm(dataset, desc=f"Evaluating {run_name}")):
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

            prediction = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            all_predictions.append(prediction)
            all_references.append(reference)

    # Compute metrics
    if not all_references:
        return {"error": "No valid samples"}

    computed_cer = cer(all_references, all_predictions)
    computed_wer = wer(all_references, all_predictions)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    results = {
        "run_name": run_name,
        "cer": round(computed_cer, 4),
        "wer": round(computed_wer, 4),
        "phonetic_accuracy": round(1.0 - computed_cer, 4),
        "num_samples": len(all_references),
        "avg_latency_sec": round(avg_latency, 4),
        "total_time_sec": round(sum(latencies), 2),
    }

    # Save results
    results_dir = config.results_dir / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Save some example predictions
    examples = []
    for ref, pred in zip(all_references[:20], all_predictions[:20]):
        examples.append({"reference": ref, "prediction": pred})
    with open(results_dir / "examples.json", "w") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"\n[{run_name}] CER: {computed_cer:.4f} | WER: {computed_wer:.4f} | "
          f"Phonetic Acc: {1-computed_cer:.4f} | Avg Latency: {avg_latency:.3f}s")

    return results
