# Review 3: Writing and Presentation

**Paper**: Jamo-LoRA: Auto-Researched Adaptation for On-Device Korean Speech Recognition

**Reviewer Role**: Writing, presentation, and claims expert

**Score**: Weak Reject

**Confidence**: 4/5

---

## Summary

The paper proposes "Jamo-LoRA," described as an automated adaptation framework that uses LoRA to fine-tune Whisper for Korean ASR on consumer hardware, with a meta-optimization loop ("AutoResearch") that navigates the trade-off between phonetic accuracy and semantic coherence. The writing is verbose but structurally broken: entire sections are duplicated, key results are missing from the tables, figures are repeated, and the central claims are not supported by the evidence presented. In its current form, the paper is not ready for publication.

---

## 1. CLARITY

### Major Issues

- **Excessive jargon masking thin content.** The paper introduces branded terminology ("Run 4 Equilibrium," "AutoResearch loop," "phonetic-semantic inversion") that sounds impressive but obscures the fact that the underlying method is a simple hyperparameter sweep over LoRA rank. Calling a 6-run grid search an "AutoResearch loop" and a "meta-optimization agent" is misleading.

- **Vague method descriptions.** Section 3.1 introduces a composite loss function L_total = L_CE + lambda * L_sem but never specifies: (a) what L_sem actually is (just "e.g., based on a language model's perplexity"), (b) how lambda is set, (c) whether this composite loss is actually used during training or only as a post-hoc evaluation criterion. This distinction is critical -- if L_sem is only used for evaluation and selection, then the training procedure is standard LoRA, not a novel method.

- **The "Jamo" component is underspecified.** Section 3.2 claims the tokenizer vocabulary is augmented with explicit Jamo tokens. This is potentially the most novel aspect of the work, yet it receives only two sentences. How many tokens were added? What was the vocabulary size before and after? How were the new embeddings initialized? Was the tokenizer truly modified or is this aspirational?

- **Inconsistent narrative voice.** The paper oscillates between confident claims ("a novel automated adaptation framework") and hedging ("hypothetical trade-off curve" in Section 5.1). If the trade-off curve is hypothetical, then the central finding of the paper is hypothetical.

### Minor Issues

- The abstract claims a "50% relative improvement" (0.30 to 0.45), but Section 4.3 and 7.1 claim a "30% relative improvement" for Run 4. These are different runs with different claims, creating confusion about the headline result.
- "Linguistically unstable" (Section 4.3) is not a standard term and is not defined.
- The phrase "semantic drift guardrail" implies an active mechanism during training, but the described method appears to be post-hoc selection.

---

## 2. STRUCTURE

### Critical Structural Defects

The paper has a **severely broken structure** with duplicated sections:

- **Section 3 (Method) appears twice** -- once starting at line 39 and again at line 130. The content is nearly identical with minor wording variations.
- **Section 4 (Experiments) appears twice** -- lines 66-97 and lines 161-191. Same duplication.
- **Section 5 (Results & Analysis) appears twice** -- lines 109-115 and lines 195-202.
- **Section 6 (Discussion) appears twice** -- lines 117-121 and lines 207-211.
- **Section 7 (Limitations) appears twice** -- once as Section 7 and once as Section 9.
- **Section 8 (Conclusion) appears twice** -- once as Section 8 and once as Section 10.
- **There is a standalone Section 7 (Results)** that is different from the duplicated Sections 5 -- creating three results-like sections total.

The numbering is also inconsistent: after the first pass (Sections 1-8), the paper restarts with Sections 3-10, including a new Section 7 (Results) that overlaps with but differs from the earlier Section 5 (Results & Analysis). This strongly suggests the paper was assembled by concatenating multiple drafts without proofreading.

### Recommended Structure

A clean version should follow: Abstract, 1. Introduction, 2. Related Work, 3. Method, 4. Experimental Setup, 5. Results, 6. Discussion, 7. Limitations, 8. Conclusion. Each section should appear exactly once.

---

## 3. FIGURES AND TABLES

### Tables

- **Table 1 is presented twice** and in both instances has critical missing values (marked "---") for Standard LoRA and Jamo-LoRA Run 4. These are the two most important comparison points. Without them, the paper's central claim (Run 4 is the optimal trade-off) has no quantitative support in the main comparison table.

- **Table 2 (Per-Regime Analysis)** is the only table with complete data for multiple configurations. However, it appears only in the second version of the results section and provides no confidence intervals or statistical tests.

### Figures

- **Figure 6 and Figure 7** are identical (both "fig_architecture_overview.png"), appearing back-to-back with no explanation. This is clearly a copy-paste error.

- **Figure 2 (Component Analysis)** and **Figure 3 (Efficiency Scatter)** each appear twice due to section duplication.

- **Figure 1 (Framework Overview)** is referenced in the method section but placed after the duplicated method section, making it hard to locate.

- No figure shows the actual trade-off curve (Phonetic Accuracy vs. Semantic Coherence across runs), which is supposedly the paper's main finding. Section 5.1 even admits the curve is "hypothetical."

### What Is Missing

- A clear trade-off curve plot (the paper's core finding) with actual data points for all 6 runs.
- Training curves (loss over epochs) for at least the key configurations.
- Example transcriptions showing the qualitative difference between Run 4 and Run 6 outputs.
- A table showing all 6 runs with complete metrics (not just Runs 1, 4, and 6 with missing values).
- Error bars or confidence intervals on any reported metric.
- Comparison against published Korean ASR benchmarks (e.g., KsponSpeech CER numbers).

---

## 4. CLAIMS vs. EVIDENCE

### Overclaims

1. **"Novel automated adaptation framework"**: The described method is a sequential hyperparameter sweep over LoRA rank (6 runs, r=4 to r=64) with post-hoc selection based on two metrics. This is not novel -- it is standard practice. The "AutoResearch agent" that "analyzes the gradient of the trade-off" is described algorithmically but there is no evidence it operates differently from manual sequential experimentation.

2. **"50% relative improvement"**: The abstract claims 0.30 to 0.45, which is Run 6 (the over-optimized configuration that the paper itself argues against deploying). The paper then advocates for Run 4, but Run 4's actual metrics are missing from the tables. The abstract's headline number contradicts the paper's own recommendation.

3. **"Phonetic-aware adaptation strategy that modifies the standard LoRA objective"**: The composite loss L_total is described but there is no evidence it was implemented. The training procedure described in Section 3.4 mentions only standard HuggingFace peft/transformers with no custom loss function. If L_sem was only used for model selection (not training), then the LoRA objective was not modified.

4. **"Statistically significant negative correlation"** (Section 7.1): No statistical test is reported. With 6 data points (of which only 3 have reported values), claiming statistical significance is unfounded.

5. **"Democratization of research tools"**: Fine-tuning LoRA on a laptop is well-established practice since 2023. This is not a contribution of this paper.

### Unsupported Claims

- The paper repeatedly discusses consonant assimilation rules but never demonstrates that Jamo-LoRA actually handles these better than the baseline.
- The "semantic drift guardrail" is described as a contribution but never shown to function differently from simply choosing an intermediate-rank LoRA configuration.
- No comparison is made to any published Korean ASR result, making it impossible to contextualize the reported numbers.

---

## 5. TITLE AND ABSTRACT

### Title: "Jamo-LoRA"

The name implies a LoRA method specifically designed around Jamo (Korean phonemic units). However:

- The Jamo tokenizer augmentation (the only Jamo-specific component) receives two sentences of description and no ablation.
- There is no experiment comparing Jamo-tokenized LoRA vs. standard-tokenized LoRA, which would be the minimum evidence needed to justify the name.
- The actual experiments appear to be standard LoRA runs at different ranks on a Whisper model with Korean data. The results would be the same regardless of whether Jamo tokens were used.

**Recommendation**: The title overpromises. Until there is evidence that the Jamo component contributes meaningfully, the paper describes "LoRA rank selection for Korean Whisper fine-tuning," not "Jamo-LoRA."

### Abstract

- The abstract is 180 words, which is reasonable, but it front-loads jargon and buries the actual result.
- The "50% relative improvement" headline is from Run 6, which the paper itself rejects as unsuitable for deployment. This is misleading.
- The abstract should state the Run 4 result, but that result is missing from the paper's own tables.

---

## 6. RELATED WORK

### Coverage

The related work section covers three relevant areas (efficient speech adaptation, Korean morphology, automated HPO) and cites relevant papers (Whisper, OWSM, LoRA-Whisper). The structure is adequate.

### Major Omissions

- **KsponSpeech and established Korean ASR benchmarks**: The paper evaluates on a self-curated 5-hour YouTube dataset but does not reference any standard Korean speech corpus. KsponSpeech (Bang et al., 2020) is the most widely used Korean conversational speech corpus and should be cited and ideally used for evaluation.

- **Other PEFT methods for speech**: No mention of adapter tuning, prefix tuning, or prompt tuning applied to speech models. The paper should justify why LoRA was chosen over alternatives.

- **Whisper fine-tuning studies on Korean**: There is a growing body of work fine-tuning Whisper specifically for Korean (e.g., work from ETRI, KAIST groups). These are not cited.

- **QLoRA (Dettmers et al., 2023)**: The paper uses 8-bit quantization with LoRA but does not cite or discuss QLoRA, which is the standard reference for this combination.

- **Multi-objective optimization in NLP**: The paper frames its contribution as multi-objective optimization but cites no MOO literature (e.g., Pareto-optimal methods, NSGA-II, or multi-objective Bayesian optimization).

### Citation Format

References use informal bracket notation ([song2024lorawhisper]) that looks like BibTeX keys rather than proper citations. This needs to be converted to a standard format (numbered or author-year).

---

## Detailed Recommendations for Revision

1. **Deduplicate the paper.** Remove all repeated sections. The paper should be approximately half its current length.

2. **Fill in all missing table values.** If the experiments were run, report the numbers. If they were not run, do not reference them.

3. **Clarify whether L_sem is a training loss or evaluation metric.** This distinction changes whether the contribution is "a novel training objective" or "a model selection criterion."

4. **Add an ablation isolating the Jamo tokenizer contribution.** Compare LoRA with and without Jamo token augmentation at the same rank to justify the paper's name.

5. **Report results on a standard Korean ASR benchmark** to enable comparison with prior work.

6. **Remove or substantiate the "50% improvement" claim.** Report the actual Run 4 numbers prominently.

7. **Add error bars, confidence intervals, or multiple random seeds** to support claims of statistical significance.

8. **Fix all figure issues**: remove duplicates, ensure each figure is referenced in text, and add the missing trade-off curve.

---

## Final Assessment

The paper addresses a relevant problem (efficient Korean ASR adaptation on consumer hardware) and the general research direction is sound. However, in its current state, the manuscript suffers from critical structural defects (duplicated sections), missing experimental data in key tables, overclaimed contributions, and insufficient evidence for its central claims. The "Jamo" component that gives the paper its name is essentially unvalidated. The writing volume is high but the information density is low. A major revision addressing all the above points would be necessary before reconsideration.

**Score**: Weak Reject
**Confidence**: 4/5 (I am confident in this assessment; the structural and evidentiary issues are clear-cut)
