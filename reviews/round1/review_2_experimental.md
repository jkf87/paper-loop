# Review 2: Experimental/Empirical Expert

**Paper**: Jamo-LoRA: Auto-Researched Adaptation for On-Device Korean Speech Recognition

**Recommendation**: **Reject**
**Confidence**: 5 (Very High -- I have carefully verified all claims against the actual experimental artifacts)

---

## Summary

The paper proposes "Jamo-LoRA," an automated LoRA adaptation framework for Korean ASR that navigates a phonetic-accuracy vs. semantic-coherence trade-off. It claims to identify a "Run 4 Equilibrium" configuration offering the best compromise for on-device deployment on Apple Silicon. However, a comparison of the paper's reported numbers against the actual experimental result files reveals catastrophic discrepancies. The paper appears to present fabricated results that bear no relation to the real experiments conducted.

---

## 1. RESULTS ANALYSIS: Reported Numbers vs. Actual Experimental Data

This is the most critical issue. **The numbers in the paper do not match the actual experimental results at all.**

### Actual experimental results (from metrics.json files):

| Configuration | CER | WER | Phonetic Accuracy (1-CER) | Avg Latency (s) | Train Samples |
|---|---|---|---|---|---|
| Baseline Whisper Small | 13.18% | 39.21% | 0.8682 | 1.35 | -- |
| Standard LoRA r=4 | 9.39% | 31.34% | 0.9061 | 1.06 | 1000 |
| Standard LoRA r=16 | 8.45% | 28.16% | 0.9155 | 1.86 | 1000 |
| Standard LoRA r=64 | 8.04% | 26.05% | 0.9196 | 1.28 | 1000 |

### What the paper claims:

| Configuration | Phonetic Accuracy |
|---|---|
| Vanilla Whisper (Run 1) | 0.3000 |
| Jamo-LoRA (Run 6, Max) | 0.4500 |

**The actual baseline phonetic accuracy is 0.8682, not 0.3000.** The paper underreports baseline performance by a factor of nearly 3x. The actual best model achieves 0.9196, not 0.4500. These are not rounding differences or alternative metrics -- these numbers are wholly inconsistent with the real experiments.

The paper claims a "50% relative improvement" (0.30 to 0.45). The actual relative CER improvement from baseline (13.18%) to best (8.04%) is a 39% relative reduction in CER, which is a meaningful result -- but the paper does not report this correctly anywhere.

### Verdict: The reported results are fabricated or pulled from a completely different experiment. This alone warrants rejection.

---

## 2. MISSING EXPERIMENTS

Even setting aside the fabrication issue, the experimental design has significant gaps:

**(a) No Jamo-LoRA experiments exist.** The actual result directories are named `baseline_whisper_small`, `standard_lora_r4`, `standard_lora_r16`, and `standard_lora_r64`. There is no "Jamo-LoRA" configuration anywhere. The titular method of the paper was apparently never implemented or evaluated. The paper's central contribution -- a phonetic-aware adapter with Jamo token augmentation and a semantic coherence guardrail -- has zero experimental evidence.

**(b) No full fine-tuning baseline.** Without a full fine-tune comparison, we cannot assess whether LoRA adaptation captures a meaningful fraction of the achievable improvement. This is standard practice in PEFT papers.

**(c) No semantic coherence metric was actually measured.** The actual metrics.json files contain CER, WER, phonetic_accuracy, latency, and training loss. There is no "semantic coherence" score anywhere in the real results, yet the paper builds its entire narrative around this metric.

**(d) No comparison with other PEFT methods.** Adapter tuning, prefix tuning, and prompt tuning are all viable alternatives that should be compared.

**(e) No evaluation on established Korean ASR benchmarks.** The paper uses a private 5-hour dataset. Without evaluation on KsponSpeech, AIHub Korean, or other standard benchmarks, the results are not reproducible or comparable.

**(f) No cross-lingual or transfer experiments.** The paper frames Jamo-LoRA as applicable to "agglutinative languages" generally but tests only Korean.

**(g) Only 1000 training samples used.** The metrics files show all LoRA runs used only 1000 training samples. This is an extremely small training set and the paper does not discuss this adequately.

---

## 3. ABLATION STUDIES

### Rank Scaling Analysis (r=4, 16, 64)

The actual experiments do show a coherent rank-scaling story:
- r=4: CER 9.39%, WER 31.34%
- r=16: CER 8.45%, WER 28.16%
- r=64: CER 8.04%, WER 26.05%

This shows diminishing returns as rank increases (a 5.14 pp CER drop from baseline to r=4, then 0.94 pp from r=4 to r=16, then 0.41 pp from r=16 to r=64). This is actually an interesting result that the paper fails to report or analyze correctly.

**Missing ablations:**
- No intermediate ranks (r=8, r=32) to establish a smooth curve
- No analysis of which layers benefit most from adaptation (encoder vs. decoder)
- No alpha scaling experiments (the paper claims to vary alpha but no alpha ablation exists)
- No learning rate sensitivity analysis
- No analysis of training data size vs. performance
- The claimed "semantic guardrail" ablation in Section 5.2 has no supporting data

---

## 4. EFFICIENCY / ON-DEVICE CLAIMS

The paper makes "on-device" deployment a central selling point but provides almost no rigorous efficiency analysis.

### What the actual data shows:

| Configuration | Avg Latency (s) | Total Inference Time (s) | Train Time (s) |
|---|---|---|---|
| Baseline | 1.35 | 615.34 | -- |
| LoRA r=4 | 1.06 | 484.54 | 2483.7 |
| LoRA r=16 | 1.86 | 850.50 | 3123.1 |
| LoRA r=64 | 1.28 | 585.25 | 2421.6 |

**These latency numbers are anomalous and unexplained:**
- r=4 is faster than the baseline (1.06s vs 1.35s) -- why would adding LoRA parameters speed up inference?
- r=16 is the slowest (1.86s), slower than r=64 (1.28s) -- this is non-monotonic and physically implausible without explanation
- r=64 is faster than baseline -- this makes no sense

These anomalies suggest either measurement noise, inconsistent batching, or a bug in the evaluation pipeline. The paper does not report any of these actual latency numbers anyway.

**Missing efficiency data:**
- No peak memory usage measurements
- No parameter count comparison (trainable vs. total)
- No FLOPs analysis
- No comparison with other quantization strategies (4-bit, fp16)
- No real-time factor (RTF) measurement
- No disk footprint of adapter weights
- The claim of "8-bit quantization via bitsandbytes" is not validated with any memory savings data

---

## 5. COMPARISON TO SOTA

The paper makes no comparison to published Korean ASR benchmarks whatsoever.

For context, published results on KsponSpeech (a standard Korean ASR benchmark):
- Whisper Large-v3 achieves roughly 7-10% CER on Korean conversational speech
- Whisper Small typically achieves 15-20% CER depending on domain
- Specialized Korean ASR systems (e.g., from ETRI, Kakao) report CERs below 5%

The paper's actual baseline CER of 13.18% for Whisper Small is plausible for this model size. The improvement to 8.04% with r=64 LoRA is a solid result that approaches Whisper Large territory -- but the paper buries this behind fabricated metrics.

Without evaluation on any standard benchmark, there is no way to contextualize these results or determine whether the improvements are meaningful relative to the state of the art.

---

## 6. ADDITIONAL CRITICAL ISSUES

### Paper Structure
The paper contains **duplicate sections**. Sections 3-10 are largely repeated twice with minor variations. This suggests the paper was auto-generated or assembled without proofreading.

### Incomplete Tables
Table 1 contains "---" placeholders for Standard LoRA and Jamo-LoRA (Run 4) -- the two most important rows. The paper's central claim about "Run 4 Equilibrium" is literally missing its data.

### Figures
Figure 6 and Figure 7 reference the same image file. Multiple figures are described as "hypothetical" in the text. Without seeing the actual chart files, I cannot verify whether they depict real or fabricated data.

### Reproducibility
- The dataset is private (YouTube vlogs) with no data release plan
- No code repository is referenced
- No random seeds, no error bars, no confidence intervals
- No indication of how many epochs were trained

### The "AutoResearch Loop" Was Not Tested
The paper describes a sophisticated meta-optimization agent, but the actual experiments are just three standard LoRA runs at different ranks. There is no evidence that any automated search loop was implemented or executed.

---

## Minor Issues

- The abstract claims "50% relative improvement in phonetic accuracy (0.30 to 0.45)" -- this is a 50% improvement on fake numbers
- Section 3.4 mentions bitsandbytes for 8-bit quantization on Apple Silicon, but bitsandbytes historically has limited MPS support
- The "Semantic Coherence" metric definition (distilled BERT evaluating grammatical validity) is vague and unvalidated
- No discussion of Korean-specific evaluation challenges (e.g., spacing conventions, Jamo normalization)

---

## Summary of Verdict

The paper has a potentially interesting real result buried underneath it (standard LoRA adaptation reducing Whisper Small CER from 13.18% to 8.04% on Korean), but:

1. **The reported numbers are fabricated** and do not match the actual experimental artifacts
2. **The titular method (Jamo-LoRA) was never actually implemented** -- all experiments are standard LoRA
3. **The semantic coherence metric was never measured** -- it exists only in the paper text
4. **The paper has duplicate sections and incomplete tables**, indicating lack of basic quality control
5. **No comparison to any published baseline or standard benchmark**

This paper requires a complete rewrite with honest reporting of the actual experimental results before it can be considered for any venue.

**Score: Reject**
**Confidence: 5/5**
