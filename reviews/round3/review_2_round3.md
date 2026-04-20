# Review 2 (Round 3): Experimental/Empirical Expert

**Paper**: LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study on Consumer Hardware

**Review history**:
- Round 1: Reject (fabricated data, fictional Jamo-LoRA method)
- Round 2: Weak Accept (honest revision, but narrow experimental coverage)
- **Round 3: Accept (workshop) / Weak Accept (main track)**
- **Confidence: 4 (High)**

---

## Summary of Round-3 Changes

The authors have made a second substantive revision that directly targets the three most concrete experimental gaps flagged in the round-2 review:

1. The rank sweep has been extended from three points ({4, 16, 64}) to five ({4, 8, 16, 32, 64}), filling in both intermediate ranks previously requested.
2. A multi-seed study has been added at r=16 with four seeds (42, 123, 456, 789), yielding a mean CER of 9.15% with a standard deviation of 0.48 percentage points and a 95% CI of [8.39, 9.91].
3. The previously missing rank-scaling figure is now present, and a new multi-seed dispersion figure (fig_multiseed.png) has been added.
4. The narrative has been reframed: the paper no longer claims r=16 is "optimal" on the basis of a single run; instead, it explicitly flags the original seed-42 r=16 result (8.45%) as a lower-tail outlier and shifts the central contribution toward a methodological warning about single-seed rank sweeps.

This is an unusually honest and scientifically mature revision. Rather than papering over the r=8 anomaly, the authors use it as direct motivation for the multi-seed experiment and then show that both the r=8 dip and the r=16 seed-42 low point are plausibly consistent with seed variance. The paper's center of gravity has shifted from "which rank is best" to "why single-seed LoRA sweeps on small data are unreliable," which is a more defensible and genuinely useful finding.

---

## Assessment of Round-2 Residual Issues

### Item 9 / "Only three rank values" — RESOLVED
Five ranks are now reported (r in {4, 8, 16, 32, 64}). Table 2 quantifies marginal gains step by step, and Figure fig_rank_scaling visualizes the curve. The diminishing-returns claim past r=16 is now supported by four step transitions rather than two. The r=8 non-monotonicity (worse than r=4) is surfaced rather than hidden and is explicitly used to motivate the multi-seed analysis. This is exactly how an honest empirical paper should handle an uncomfortable data point.

### Item 11 / "Single runs, no confidence intervals" — PARTIALLY RESOLVED
Only r=16 has multi-seed coverage; r in {4, 8, 32, 64} remain single-seed. The authors are transparent about this in Limitations item 1, and the abstract, results, and discussion all carefully qualify non-r=16 numbers as point estimates. Given that each run takes roughly 45-55 minutes on an M4 laptop, a full 5 x 4 = 20-run sweep is a non-trivial compute commitment, and partial coverage with explicit acknowledgment is a reasonable compromise for a workshop-scope paper.

However, this partial coverage does create one interpretive tension the paper has not fully closed: the 95% CI at r=16 is [8.39, 9.91], which contains the seed-42 single-run numbers for r=32 (8.21) and r=64 (8.04). Strictly speaking, the paper cannot currently claim that r=64 is better than r=16 at any statistical confidence level, because the r=64 point estimate sits inside the r=16 confidence interval. Section 6 does hedge ("modest gains whose practical significance is within the observed seed variance"), but the abstract still reports "39% relative improvement" at r=64 without the same caveat. A one-sentence qualifier in the abstract would close this gap.

### Item 17 / "Missing figure" — RESOLVED
fig_rank_scaling, fig_efficiency, and the new fig_multiseed are all referenced via includegraphics. Assuming the PNG files render correctly, this concern is fully addressed.

### Latency anomaly — UNCHANGED (appropriately)
Still acknowledged in Limitations item 7. I continue to agree with the round-2 assessment that this is honest and appropriate; a full latency re-measurement with confidence intervals is out of scope for a revision of this size.

### Novelty — UNCHANGED but RE-CONTEXTUALIZED
In round 2 I flagged limited novelty ("standard LoRA on standard model/dataset"). The round-3 reframing partially addresses this concern by repositioning the contribution. The paper is no longer asking readers to find novelty in applying LoRA to Whisper-Small-Korean; it is asking readers to take seriously the methodological claim that CER differences below ~0.5 percentage points in this regime are within seed noise and that single-seed sweeps can produce inverted orderings. That is a legitimate (if modest) empirical contribution to how the community reports LoRA hyperparameter studies on small datasets. It is the right kind of scope for a workshop paper.

---

## New Strengths Introduced in Round 3

- **The methodological reframing is the right call.** Shifting the central message from "r=16 is the sweet spot" to "multi-seed evaluation is necessary" is both more defensible given the evidence and more generally useful to the field.
- **The r=8 explanation is scientifically honest.** Rather than quietly dropping the anomalous point or blaming a bug, the authors show that 10.27% is within roughly 2.3 standard deviations of the r=16 mean and attribute it plausibly to seed variance. This is the correct statistical framing.
- **The "seed 42 r=16 was an outlier" admission is noteworthy.** It would have been easy to quietly replace 8.45% with the seed-mean 9.15% in Table 1 and avoid the awkward discussion. Instead, the paper keeps the original number, flags it as a lower-tail outlier, and uses the discrepancy as evidence for its main claim. This is mature scientific writing.
- **Table 2 marginal-CER column is a nice addition.** Making the step-by-step deltas explicit (including the negative 0.88 pp at r=4 -> r=8) forces the reader to engage with the non-monotonicity directly.
- **The 95% CI computation is reported.** [8.39, 9.91] is a t-interval on four samples and is the right statistic to report; the paper does not overclaim by presenting a z-interval.

---

## Remaining Weaknesses

These are all minor relative to where the paper started, and none block acceptance at a workshop venue.

1. **Internal consistency around r=64 as "best."** The abstract and conclusion still headline "8.04% CER at r=64, 39% relative improvement," but Section 6 concedes this improvement is within the r=16 seed variance. Consider adding one qualifier to the abstract, e.g., "r=64 achieves the best single-run CER of 8.04%, though this difference is within the r=16 seed variance (0.48 pp std)."

2. **Section 4.2 still says "three rank configurations."** Line 75 of paper.tex reads: "We evaluate three rank configurations (r in {4, 16, 64})..." This is stale text from the previous revision; it should now read "five rank configurations (r in {4, 8, 16, 32, 64})." This is a copy-editing miss, not a scientific issue, but should be fixed before submission.

3. **Asymmetric multi-seed coverage leaves a claim slightly wobbly.** The sentence in Section 5.3 -- "the mean across four seeds (9.15%) is statistically indistinguishable from our r=4 seed-42 result (9.39%)" -- compares a four-seed mean at r=16 against a one-seed point at r=4. Strictly, "statistically indistinguishable" requires a test, not just CI containment of a point estimate. Softening to "is within one standard deviation of the r=4 seed-42 point estimate" would be more precise.

4. **No full-sweep multi-seed.** Ideally, the paper would run at least two additional seeds at r in {4, 8, 32, 64} to confirm that r=8 really is within seed variance rather than a systematic effect. I recognize this is costly (~4 additional hours on the M4), but even two extra seeds at r=8 specifically would convert the most speculative claim in the paper (r=8 anomaly attributed to seed variance) into a supported one.

5. **Still no full fine-tuning baseline, no other PEFT method, no memory profile.** These were flagged in round 2, are acknowledged in Limitations, and remain out of scope. For a workshop venue this is acceptable; for a main-conference venue it would not be.

6. **Abstract still uses "39% relative improvement" framing.** Given the paper's own argument that single-run numbers are unreliable, leading with a single-run point-estimate improvement in the abstract is slightly at odds with the methodological thesis. Consider reporting both: "13.18% -> 8.04% at r=64 single-run, 13.18% -> 9.15% +/- 0.48 pp at r=16 multi-seed."

---

## Has the paper crossed the workshop-acceptance threshold?

**Yes.** The three concrete round-2 asks were (a) more rank points, (b) multi-seed confidence intervals, and (c) the missing figure. All three have been addressed, (a) and (c) fully and (b) partially but with transparent acknowledgment. The remaining gaps (full-sweep multi-seed, other PEFT baselines, memory profiling) are all flagged in Limitations and are reasonable future work for a workshop-scope empirical paper.

More importantly, the paper is now making a claim its evidence actually supports. That claim -- "in the 1k-sample / 1-epoch / Whisper-Small regime, CER differences on the order of 0.5 percentage points between LoRA ranks are within seed noise, and single-seed sweeps can invert the true ordering" -- is modest, honest, correct given the data, and practically useful to practitioners doing LoRA hyperparameter selection on small Korean ASR datasets. The paper's diagnostic value (don't trust single-seed LoRA sweeps at small scale) is arguably more broadly applicable than a hypothetical "r=16 is optimal" result would have been.

---

## Score and Confidence

- **Workshop track: Accept.** The paper is within scope, honestly reported, experimentally tightened where it mattered, and makes a defensible methodological contribution. I would be happy to see this at a PEFT, efficient-ML, or low-resource-speech workshop.
- **Main conference (top venue): Weak Accept / Borderline.** The experimental coverage is still narrow (one model size, one dataset, one PEFT method, partial multi-seed). The novelty remains primarily methodological-diagnostic rather than methodological-innovative. A main-track version would need a denser multi-seed grid and at least one additional PEFT baseline.

**Final recommendation: Accept (workshop) / Weak Accept (main track).**
**Confidence: 4/5.**

The author team has now demonstrated, across two revisions, the willingness to (1) replace fabricated results with honest ones, (2) extend experiments in response to reviewer asks, and (3) reframe claims when the new evidence does not support the old narrative. These are the behaviors the review process is meant to reward, and I am comfortable recommending acceptance at the workshop level on that basis.
