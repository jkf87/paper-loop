# Review 1: Methodology Expert Review

**Paper**: Jamo-LoRA: Auto-Researched Adaptation for On-Device Korean Speech Recognition

**Reviewer**: Reviewer 1 (Methodology Expert)

**Score**: **Reject**

**Confidence**: 5 (Very High -- I have carefully compared the paper's claims against the actual experimental results files)

---

## Summary

The paper proposes "Jamo-LoRA," a framework that uses an AutoResearch loop to optimize LoRA hyperparameters for Korean ASR adaptation on consumer hardware. The claimed contributions include a phonetic-semantic trade-off analysis, an automated hyperparameter search, and a "Run 4 Equilibrium" finding. However, upon careful examination, the paper contains critical integrity issues: the reported numbers in the paper are fabricated and directly contradict the actual experimental results. The methodology as described does not match what was actually implemented, and the paper's central narrative is built on false data.

---

## 1. METHODOLOGY

### 1.1 Critical Integrity Issue: Fabricated Results

This is the most serious finding of this review. The paper reports:

- Baseline Whisper: Phonetic Accuracy = **0.30** (i.e., CER = 0.70)
- Jamo-LoRA Run 6: Phonetic Accuracy = **0.45** (i.e., CER = 0.55)

The actual experimental results files show:

| Configuration | CER | Phonetic Accuracy (1-CER) |
|---|---|---|
| baseline_whisper_small | 0.1318 | **0.8682** |
| standard_lora_r4 | 0.0939 | **0.9061** |
| standard_lora_r16 | 0.0845 | **0.9155** |
| standard_lora_r64 | 0.0804 | **0.9196** |

The real baseline phonetic accuracy is **0.87**, not 0.30. The real best result is **0.92**, not 0.45. The paper underreports the baseline by nearly 3x to fabricate a dramatic "50% relative improvement" narrative. The actual relative improvement from baseline to best LoRA is approximately 5.9% relative CER reduction -- a respectable but far less dramatic result.

This discrepancy alone warrants rejection. The paper's entire narrative -- the "Run 4 Equilibrium," the "phonetic-semantic inversion," the "50% relative improvement" -- is built on numbers that do not exist in the actual experimental data.

### 1.2 The "Jamo-LoRA" Method Does Not Exist in the Experiments

The paper describes a novel "Jamo-LoRA" architecture with Jamo tokenization augmentation and a composite loss function with a semantic coherence term. However, the actual results directories are named `standard_lora_r4`, `standard_lora_r16`, and `standard_lora_r64`. There is no evidence that any "Jamo-LoRA" method was actually implemented or evaluated. What was actually run appears to be straightforward standard LoRA fine-tuning at different ranks. The paper appears to relabel standard LoRA as "Jamo-LoRA" without any distinguishing implementation.

### 1.3 The Composite Loss Function is Unsubstantiated

The paper defines $L_{total} = L_{CE} + \lambda \cdot L_{sem}$ but never specifies:
- What value of $\lambda$ was used
- How $L_{sem}$ was computed during training (the paper says "based on a language model's perplexity" but this is vague)
- Whether this loss was actually implemented in training (given that the results directories suggest standard LoRA was used)
- There is no "Semantic Coherence" metric in any of the actual results JSON files

### 1.4 Target Module Selection

The paper states LoRA targets "the projection layers of the decoder, focusing on the mapping from the audio encoder outputs to the token embeddings." This is insufficiently specific. Which exact weight matrices? q_proj, k_proj, v_proj, out_proj? Cross-attention only, or self-attention too? Without this detail, the method cannot be reproduced.

### 1.5 Jamo Tokenization Claims

The paper claims to "augment the standard tokenizer's vocabulary with explicit Jamo tokens" to force the adapter to learn phoneme-level mappings. There is no evidence this was actually done. No tokenizer configuration is provided. No vocabulary size comparison (before/after augmentation) is given. This is a significant architectural claim with zero supporting evidence.

---

## 2. EXPERIMENTAL DESIGN

### 2.1 Incomplete Results Table

Table 1 in the paper contains multiple "---" entries for Standard LoRA and Jamo-LoRA Run 4 -- the two most critical rows. A paper cannot claim a method is superior when it literally does not report the comparison numbers. This is an unfinished draft being presented as a complete paper.

### 2.2 Missing Baselines

- No comparison with full fine-tuning (even on a subset) to establish an upper bound.
- No comparison with other PEFT methods (Adapter, Prefix-Tuning, IA3).
- No comparison with other Korean ASR systems or publicly available models fine-tuned for Korean.
- The "Standard LoRA" baseline uses only r=16. The actual experiments tested r=4, r=16, and r=64, but the paper does not clearly report these as baselines.

### 2.3 The "Semantic Coherence" Metric

The secondary metric ("Semantic Coherence" from a distilled BERT model) is never validated. There is no correlation with human judgments. More critically, this metric does not appear in any of the actual results JSON files, suggesting it was never computed. The entire "phonetic-semantic trade-off" narrative may be a post-hoc fabrication.

### 2.4 Dataset Issues

- 5 hours of audio from "YouTube vlogs and technical discussions" -- no details on speaker count, demographics, recording conditions, or annotation process.
- No dataset statistics (utterance length distribution, vocabulary coverage).
- No mention of whether the dataset is publicly available for reproducibility.
- Training was on 1000 samples (per the JSON files), but the paper does not mention this number.

---

## 3. STATISTICAL RIGOR

### 3.1 N=457 Test Samples

While 457 samples is not inherently problematic for CER evaluation, the paper provides zero statistical analysis:
- No confidence intervals on any metric.
- No significance tests between configurations.
- No standard deviations across runs with different seeds.
- The actual improvements between LoRA ranks are small (CER: 0.0939 -> 0.0845 -> 0.0804). Without confidence intervals, it is impossible to know if these differences are statistically significant.

### 3.2 Single-Run Evaluation

Each configuration appears to have been run exactly once (one JSON file per config). There is no assessment of variance due to random initialization, data ordering, or other stochastic factors.

### 3.3 Correlation Claim Without Evidence

The paper claims "a strongly inversely correlated ($r \approx -1.0$)" relationship between phonetic accuracy and semantic coherence. A Pearson correlation of approximately -1.0 across 6 data points is trivially achievable with any two monotonic sequences. This is not a meaningful statistical finding even if the data existed.

---

## 4. REPRODUCIBILITY

### 4.1 Missing Critical Details

The following are not specified anywhere in the paper:
- Learning rate and schedule
- Number of training epochs/steps
- Batch size
- Optimizer (Adam? AdamW? learning rate warmup?)
- LoRA alpha values used (mentioned $\alpha=32$ for the baseline only)
- LoRA dropout
- Which specific Whisper model checkpoint was used
- Quantization details (which layers quantized, calibration data)
- The "AutoResearch agent" decision rules (when exactly does it increase/decrease rank?)
- Training data preprocessing (sampling rate, audio normalization, segmentation)

### 4.2 No Code or Model Release

No mention of code availability, model checkpoints, or data release.

### 4.3 Bitsandbytes on MPS

The paper claims to use `bitsandbytes` for 8-bit quantization on Apple Silicon (MPS backend). As of 2025, `bitsandbytes` has limited MPS support. This claim needs verification -- it is possible the quantization was not actually used, or a different quantization method was employed.

---

## 5. NOVELTY

### 5.1 What Is Genuinely New

Very little. The actual experiments consist of running standard LoRA at three different ranks (r=4, r=16, r=64) on Whisper Small for Korean ASR. This is a straightforward application of existing methods.

### 5.2 What Is Claimed But Unsupported

- "Jamo-LoRA" with Jamo tokenization augmentation -- no evidence of implementation
- Composite phonetic-semantic loss function -- no evidence of implementation
- "AutoResearch loop" -- appears to be manual hyperparameter search relabeled
- "Run 4 Equilibrium" -- no Run 4 results exist in the data; the concept is built on fabricated trade-off curves
- "Semantic drift guardrail" -- the semantic coherence metric was apparently never computed

### 5.3 The "AutoResearch" Framing

Describing a manual or scripted hyperparameter sweep as an "AutoResearch agent" is misleading. The described loop (try a rank, evaluate, adjust) is standard practice and does not constitute a novel contribution. Bayesian optimization, successive halving, or even grid search would accomplish the same goal and are well-established.

---

## 6. WRITING QUALITY

### 6.1 Structural Issues

- Section 3 (Method) appears **twice** in the paper, with nearly identical content.
- Sections 4 (Experiments) and 7 (Results) also appear duplicated with slight variations.
- The paper has two Section 7s, two Section 8s.
- Figure 6 and Figure 7 reference the same image.
- Multiple references to figures that are described as "hypothetical."

### 6.2 Overclaiming

The abstract claims "50% relative improvement in phonetic accuracy (Primary Metric: 0.30 to 0.45)." The real data shows baseline accuracy of 0.87 and best accuracy of 0.92. The overclaiming is severe and systematic throughout the paper.

---

## 7. SUMMARY OF MAJOR ISSUES

1. **DATA INTEGRITY FAILURE**: The numbers reported in the paper (baseline 0.30, best 0.45) are fabricated. Real results show baseline 0.87, best 0.92. This is the most serious issue.

2. **METHOD NOT IMPLEMENTED**: The "Jamo-LoRA" method (Jamo tokenization, composite loss, semantic guardrail) appears to have never been implemented. The actual experiments are standard LoRA at different ranks.

3. **INCOMPLETE TABLES**: Critical comparison rows contain "---" placeholders. The paper was submitted in an unfinished state.

4. **DUPLICATED SECTIONS**: The paper contains duplicate Method, Experiments, Results, and Conclusion sections, suggesting it was assembled hastily without proofreading.

5. **NO STATISTICAL ANALYSIS**: Single-run experiments with no confidence intervals, significance tests, or variance estimates.

6. **MISSING HYPERPARAMETERS**: Insufficient detail for reproduction.

---

## 8. RECOMMENDATIONS FOR REVISION

If the authors wish to resubmit, they should:

1. **Report actual numbers**. The real results (CER going from 0.13 to 0.08 with LoRA) are a legitimate and useful finding. Present them honestly.

2. **Actually implement the proposed method**. If Jamo tokenization and the semantic coherence loss are part of the contribution, they need to be implemented and ablated.

3. **Add proper baselines**: full fine-tuning, other PEFT methods, existing Korean ASR systems.

4. **Provide confidence intervals** via multiple random seeds per configuration.

5. **De-duplicate sections** and proofread the paper thoroughly.

6. **Specify all hyperparameters** and release code for reproducibility.

7. **Validate the semantic coherence metric** against human judgments if it is to be used as a primary evaluation axis.

8. **Tone down the novelty claims**. A well-executed empirical study of LoRA rank selection for Korean ASR on consumer hardware is a valid contribution -- but only if presented honestly.

---

## Decision: REJECT

The paper cannot be accepted in its current form due to fabricated experimental results, an unimplemented proposed method, incomplete tables, duplicated sections, and severe overclaiming. The gap between what is claimed and what was actually done is too large for a revision cycle -- it requires fundamental rework.
