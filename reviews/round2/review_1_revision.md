# Review 1 (Revision): Methodology Expert Re-Review

**Paper**: LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study on Consumer Hardware

**Reviewer**: Reviewer 1 (Methodology Expert)

**Previous Score**: Reject

**Revised Score**: **Weak Accept**

**Confidence**: 4 (High)

---

## 1. Response to Previous Critical Issues

### 1.1 Fabricated Results -- RESOLVED

The most serious issue in the original submission was that reported numbers (baseline phonetic accuracy 0.30, best 0.45) were fabricated and contradicted the actual experimental data (baseline CER 0.1318, best CER 0.0804). The revised paper now reports the real numbers throughout: baseline CER 13.18%, best LoRA CER 8.04%, corresponding to a 39% relative improvement. These numbers are consistent with what was found in the experimental result files during the first review. The "50% relative improvement" overclaim has been removed. **This critical integrity issue has been fully resolved.**

### 1.2 "Jamo-LoRA" Relabeling -- RESOLVED

The original paper dressed up standard LoRA fine-tuning as a novel "Jamo-LoRA" method with Jamo tokenization augmentation and a composite loss function, none of which were actually implemented. The revised paper honestly titles itself "LoRA Rank Scaling for On-Device Korean ASR" and frames the work as an empirical study of standard LoRA at different ranks. No false novelty claims are made. **Resolved.**

### 1.3 Fake "Semantic Coherence" Metric -- RESOLVED

The fabricated semantic coherence metric and the "phonetic-semantic trade-off" narrative have been entirely removed. The paper now reports CER, WER, and inference latency -- standard, verifiable metrics. **Resolved.**

### 1.4 Duplicated Sections -- RESOLVED

The duplicated Method, Experiments, Results, and Conclusion sections have been eliminated. The paper now has a clean, standard structure (Introduction, Related Work, Method, Experiments, Results, Discussion, Limitations, Conclusion). **Resolved.**

### 1.5 Missing Hyperparameters -- RESOLVED

Table 1 now provides a complete hyperparameters table: optimizer (AdamW), learning rate (3e-4), batch size (4 with gradient accumulation 4), epochs (1), warmup steps (20), LoRA alpha (2r), LoRA dropout (0.1), target modules (q/k/v/out_proj, fc1, fc2), training samples (1,000), and random seed (42). This is a substantial improvement. **Resolved.**

### 1.6 Incomplete Results Table -- RESOLVED

The original Table 1 had "---" placeholders in critical rows. The revised Table 2 (main results) is complete with CER, WER, trainable parameters, training loss, and latency for all four configurations (baseline + three LoRA ranks). **Resolved.**

### 1.7 Overclaiming and Novelty Inflation -- RESOLVED

The "AutoResearch agent," "Run 4 Equilibrium," "semantic drift guardrail," and other inflated claims have been removed. The paper is now framed as a straightforward empirical study, which is appropriate for its actual contributions. **Resolved.**

### 1.8 Statistical Rigor (Single Runs) -- PARTIALLY RESOLVED

The paper now explicitly acknowledges single-run evaluation as Limitation #1 and notes that confidence intervals from multiple runs would strengthen claims. This is honest, but the underlying issue remains: the CER difference between r=16 (8.45%) and r=64 (8.04%) is only 0.41 percentage points from a single run. Whether this difference is statistically significant is unknown. The acknowledgment is appreciated, but the data limitation persists.

### 1.9 Missing Baselines (Full Fine-Tuning, Other PEFT) -- PARTIALLY RESOLVED

The paper acknowledges both of these as explicit limitations (#3 and #4). The absence of a full fine-tuning baseline and comparisons with other PEFT methods (adapters, prefix tuning, IA3) remains a gap, but the honest acknowledgment is appropriate for a workshop-level empirical study.

---

## 2. Remaining Issues

### 2.1 Minor Methodological Concerns

**Latency anomaly**: The paper reports that LoRA r=4 (1.06s) is faster than the zero-shot baseline (1.35s), and r=64 (1.28s) is faster than r=16 (1.86s). This non-monotonic pattern is acknowledged in the limitations section as likely MPS backend variability. This is the right call -- these latency numbers should not be interpreted as meaningful without repeated measurements. However, reporting them without error bars in the main results table may still mislead readers who skip the limitations section. Consider adding a footnote to Table 2 noting this.

**Alpha scaling**: The choice of alpha = 2r is stated as "standard practice," but this is not universally standard. Some practitioners use a fixed alpha (e.g., 16 or 32) across all ranks. When alpha scales with rank, increasing r also increases the effective learning rate of the LoRA updates, which confounds the interpretation of rank vs. scaling factor effects. This is a minor point but worth a sentence in the discussion.

### 2.2 Dataset Scope

The zeroth_korean dataset is read speech only, and the paper acknowledges this (Limitation #2). However, the title says "Korean Speech Recognition" without qualification. A more precise title might be "Korean Read Speech Recognition" to avoid overgeneralization.

### 2.3 Comparison to Prior Work

The discussion mentions that the zero-shot CER (13.18%) is "consistent with reported performance" and that the best LoRA result "approaches" Whisper Medium/Large performance. These are vague qualitative claims. Citing specific numbers from prior work (even from the Whisper paper itself or community benchmarks) would strengthen this section. As it stands, the reader must take the authors' word for it.

### 2.4 Code and Data Availability

The paper still does not mention code or model release. For reproducibility, even a statement of intent ("Code will be released upon publication") would be helpful.

### 2.5 Writing Polish

The paper is generally well-written in the revision. A few minor items:

- The abstract is dense and could benefit from trimming some of the numerical detail.
- The "M / %p" column header in Table 3 (efficiency) is not immediately intuitive; consider spelling out "Params per %p CER reduction."
- The references.bib file was not provided for review; the citation keys look reasonable but cannot be verified.

---

## 3. Assessment of Revised Contributions

The revised paper makes three claims:

1. **Rank scaling analysis with diminishing returns**: This is a valid empirical finding. The demonstration that going from r=16 to r=64 yields only 0.41%p CER improvement at 4x the parameter cost is practically useful, even if not surprising. The efficiency analysis (Table 3) is well-presented.

2. **Low-data regime effectiveness**: Showing that 1,000 samples and 1 epoch achieve a 39% relative CER reduction is a useful data point for practitioners, though the generalizability beyond read speech is unknown.

3. **Consumer hardware feasibility**: Demonstrating that all experiments run on Apple M4 with MPS backend in under an hour is a practical contribution, particularly for researchers without GPU access.

None of these are individually novel or surprising, but collectively they provide a useful reference for practitioners working on Korean ASR with limited resources. This is an appropriate scope for a workshop paper.

---

## 4. Overall Assessment

The revision represents a dramatic improvement over the original submission. The most critical issues -- fabricated data, fake metrics, unimplemented methods, duplicated sections, and systematic overclaiming -- have all been resolved. The paper is now an honest, well-organized empirical study that reports real numbers and acknowledges its limitations forthrightly.

The remaining weaknesses (single runs, no full fine-tuning baseline, no alternative PEFT comparisons, read speech only) are genuine limitations but are all explicitly acknowledged. The contribution is modest -- it is essentially a well-executed rank sweep of LoRA on Whisper Small for Korean -- but the practical guidelines it provides (r=16 as the efficiency sweet spot, 1,000 samples sufficing for meaningful adaptation) have value for the community.

The paper is below the bar for a top-tier conference (ICASSP, Interspeech main track) due to its limited experimental scope and lack of novelty. However, it is appropriate for a workshop paper (e.g., an Interspeech satellite workshop on efficient speech processing, or a NeurIPS workshop on efficient ML).

---

## 5. Recommendations for Further Improvement (Not Required for Acceptance)

1. Run at least 3 seeds per configuration and report mean +/- std CER.
2. Add one alternative PEFT baseline (e.g., adapter tuning) for comparison.
3. Add a brief experiment with Whisper Base or Medium to test whether the r=16 finding generalizes across model sizes.
4. Cite specific prior CER numbers on zeroth_korean or Korean Whisper benchmarks in the Discussion.
5. Add a footnote to the latency column noting unreliability due to single-pass measurement.
6. State code availability plans.

---

## Decision: WEAK ACCEPT

The paper has been transformed from a fundamentally flawed submission with fabricated data into an honest, modest, but useful empirical study. The integrity issues that warranted rejection have been fully resolved. The remaining limitations are acknowledged and are acceptable for a workshop venue. I recommend acceptance at a workshop, with the understanding that the contribution is incremental and the experimental scope is narrow.
