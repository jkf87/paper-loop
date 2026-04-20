# Review 2 (Revision): Experimental/Empirical Expert

**Paper**: LoRA Rank Scaling for On-Device Korean ASR: An Empirical Study on Consumer Hardware

**Previous Recommendation**: Reject
**Revised Recommendation**: **Weak Accept**
**Confidence**: 4 (High)

---

## Summary of Revision

The revised paper is fundamentally different from the original submission. The authors have (1) changed the title to accurately reflect the work conducted, (2) removed all fabricated metrics and the fictional "Jamo-LoRA" method, (3) reported real experimental results from the zeroth_korean dataset, (4) added a hyperparameters table, and (5) written an honest limitations section. This is a commendable and thorough revision that transforms a paper warranting rejection into a credible empirical study.

---

## Assessment of Previously Raised Issues

### Resolved Issues

1. **Fabricated results (CRITICAL -- RESOLVED).** The original paper reported wholly fictitious numbers (baseline phonetic accuracy of 0.30, best of 0.45). The revision reports the actual experimental data: baseline CER 13.18%, best CER 8.04%. All numbers in Tables 1-2 are consistent with the real metrics. This was the primary reason for rejection and it is fully addressed.

2. **Fictional method (CRITICAL -- RESOLVED).** The "Jamo-LoRA" method, which was never implemented, has been removed entirely. The paper now correctly presents itself as a study of standard LoRA rank scaling. The title, abstract, and all sections are consistent with what was actually done.

3. **Fabricated semantic coherence metric (CRITICAL -- RESOLVED).** The invented "semantic coherence" metric and its associated narrative have been removed. The paper now uses CER and WER throughout, which are standard and were actually measured.

4. **Duplicate sections (RESOLVED).** The paper is now cleanly structured with no repeated content.

5. **Incomplete tables (RESOLVED).** All table entries are populated with real data. The hyperparameter table (Table 1) is a welcome addition that aids reproducibility.

6. **Dataset transparency (RESOLVED).** The paper now identifies zeroth_korean as the dataset, reports its size (51 hours, 115 speakers), and specifies the test set size (457 samples). This is a publicly available corpus, addressing the previous reproducibility concern.

7. **Training sample size acknowledged (RESOLVED).** The 1,000-sample regime is now foregrounded as a deliberate design choice and discussed as a contribution (low-data regime adaptation), rather than being hidden.

8. **Latency anomalies (RESOLVED).** The limitations section (item 7) explicitly flags the non-monotonic latency pattern as likely MPS backend variability. This is honest and appropriate.

### Partially Resolved Issues

9. **Missing rank scaling analysis (MOSTLY RESOLVED).** The original paper failed to analyze the diminishing returns pattern that was present in the real data. The revision makes this the central finding, with Table 2 quantifying marginal CER gains and parameter efficiency. This is well done. However, intermediate ranks (r=8, r=32) are still absent, which would strengthen the claim that r=16 is optimal rather than merely being the middle data point of three.

10. **No comparison to SOTA (PARTIALLY RESOLVED).** The discussion section now contextualizes results by noting the baseline CER is "consistent with reported performance of Whisper on Korean read speech" and that the best result "approaches the performance typically associated with Whisper Medium or Large variants." This is better than before but remains qualitative. A table of published Korean ASR results would be more convincing.

### Remaining Issues

11. **Single runs, no confidence intervals.** Acknowledged in limitations (item 1) but not addressed experimentally. The CER difference between r=16 (8.45%) and r=64 (8.04%) is only 0.41 percentage points. Without multiple seeds, we cannot determine whether this difference is statistically significant. The claim that r=16 is the "optimal" trade-off point rests partly on this comparison.

12. **No full fine-tuning baseline.** Acknowledged in limitations (item 3). Without this, we do not know how much headroom LoRA leaves on the table.

13. **No comparison with other PEFT methods.** Acknowledged in limitations (item 4). Adapter tuning, prefix tuning, or IA3 comparisons would substantially strengthen the paper.

14. **Read speech only.** Acknowledged in limitations (item 2). Generalization to spontaneous speech or noisy conditions is unknown.

15. **No layer-level analysis.** The paper applies LoRA to all six module types uniformly. An ablation showing which layers (encoder vs. decoder, attention vs. FFN) contribute most to CER reduction would add analytical depth.

16. **No memory usage data.** For a paper emphasizing "on-device" deployment, peak memory consumption during training and inference is a notable omission.

17. **Missing figure.** The text references Figure 1 for rank scaling visualization, but no figure file or \includegraphics command appears in the LaTeX source. The paper should include the actual plot.

---

## New Observations on the Revised Paper

### Strengths

- **Honest framing.** The paper now makes claims commensurate with the evidence. The title ("An Empirical Study") correctly sets expectations.
- **Clear diminishing returns narrative.** Table 2 and the surrounding analysis effectively communicate the parameter efficiency story. The 11x efficiency decrease from r=4 to r=64 is a useful finding for practitioners.
- **Practical value.** The result that 1,000 samples and one epoch on a consumer laptop can reduce CER by 39% relative is genuinely useful for practitioners working with low-resource languages.
- **Thorough limitations section.** Seven specific limitations are enumerated, covering statistical validity, domain restriction, missing baselines, and the latency anomaly. This is mature scientific writing.

### Weaknesses

- **Novelty is limited.** The paper applies standard LoRA (as implemented by PEFT/Hugging Face) to a standard model (Whisper Small) on a standard dataset (zeroth_korean). The rank scaling analysis, while useful, is not a methodological contribution. The paper is best understood as a practical guideline rather than a research contribution.
- **Three data points for "scaling analysis."** The claim of diminishing returns is supported by only three rank values. A denser sweep (r in {2, 4, 8, 16, 32, 64, 128}) would make the scaling curve more convincing and the r=16 recommendation more robust.
- **Alpha scaling not ablated.** The paper sets alpha = 2r throughout. Since alpha and r jointly determine the effective learning rate of the LoRA update, varying alpha independently would better isolate the capacity effect of rank from the optimization effect of scaling.
- **WER improvement is modest relative to CER.** CER drops from 13.18% to 8.04% (39% relative), but WER drops from 39.21% to 26.05% (34% relative). The WER remains quite high. The paper does not discuss this gap or what it implies about word-boundary errors vs. character-level errors.
- **Missing figure.** Figure 1 is referenced in the text but not present in the LaTeX source. A visualization of the rank-CER-parameter trade-off would meaningfully improve the paper.

---

## Minor Issues

- The abstract states "91.55% phonetic accuracy" which is simply 1 - CER for r=16. This is a non-standard way to report ASR results and could confuse readers. CER alone suffices.
- Line 68: the LoRA scaling formula uses alpha/r, but alpha = 2r, so the effective multiplier is always 2. This should be noted explicitly, as it means changing rank does not change the scaling -- only the capacity of the low-rank approximation changes.
- The paper does not specify the Whisper variant version (v1, v2, v3). "openai/whisper-small" should be pinned to a specific version for reproducibility.
- No code repository or model checkpoint release is mentioned. For an empirical study on consumer hardware, releasing the adapter weights would significantly increase impact.

---

## Overall Assessment

The revision addresses the most egregious problems of the original submission -- fabricated data, a fictional method, and duplicate sections. What remains is an honest, if modest, empirical study. The central finding (diminishing returns of LoRA rank scaling for Korean ASR, with r=16 as a practical sweet spot) is supported by the data, practically useful, and clearly communicated.

The paper's main weakness is limited novelty: it applies an existing method (LoRA) to an existing model (Whisper) on an existing dataset (zeroth_korean) with no methodological innovation. The experimental coverage is narrow (three ranks, single seed, single dataset, single model size, single PEFT method). However, the paper is transparent about these limitations, and the practical value for the Korean ASR community is real.

For a workshop paper or empirical track, this is acceptable. For a main conference track at a top venue, the experimental breadth would need expansion (more ranks, multiple seeds, at least one additional PEFT baseline, memory profiling).

**Score: Weak Accept**
**Confidence: 4/5**

The dramatic improvement from the original submission is acknowledged and appreciated. The authors have demonstrated scientific integrity by replacing fabricated results with honest reporting, which is the single most important criterion for publishable work.
