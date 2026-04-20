# Review 1 (Round 3): Methodology Expert Re-Review

**Paper**: LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study on Consumer Hardware

**Reviewer**: Reviewer 1 (Methodology Expert)

**Round 1 Score**: Reject (fabricated data, unimplemented method, duplicated sections)
**Round 2 Score**: Weak Accept (integrity issues resolved; single-seed concern partially remaining)
**Round 3 Score**: **Accept (workshop) / Weak Accept (main track)**

**Confidence**: 4 (High)

---

## 1. Response to Round-2 Residual Concerns

The Round-2 review identified two residual methodological concerns that were only "partially resolved": (a) single-seed evaluation, and (b) the absence of alternative PEFT baselines and full fine-tuning. The authors have addressed (a) substantially and in a methodologically interesting way. They have not addressed (b), but have honestly maintained it as an explicit limitation.

### 1.1 Single-Seed Concern -- SUBSTANTIALLY RESOLVED (and turned into a contribution)

In Round 2 I wrote: "the CER difference between r=16 (8.45%) and r=64 (8.04%) is only 0.41 percentage points from a single run. Whether this difference is statistically significant is unknown."

The authors have now:

1. **Extended the rank sweep** from 3 points to 5 (r in {4, 8, 16, 32, 64}).
2. **Run four independent seeds at r=16** (42, 123, 456, 789), reporting CER 8.45 / 9.33 / 9.29 / 9.54, mean 9.15 +/- 0.48, 95% CI [8.39, 9.91].
3. **Explicitly flagged the original seed-42 r=16 result as a lower-tail outlier** and noted that the mean across four seeds is statistically indistinguishable from r=4 at seed 42 (9.39%).
4. **Reinterpreted the r=8 anomaly** (10.27%, worse than r=4) as likely seed variance rather than a genuine capacity effect, since it falls within roughly 2 sigma of the r=16 mean.
5. **Refamed the contribution** around a methodological recommendation: single-seed rank sweeps in the low-data regime can produce misleading orderings; multi-seed evaluation is necessary for robust comparison.

This is the correct response, and arguably a better response than simply re-running every rank with multiple seeds. The authors did not retrofit their narrative to defend the original point estimates -- they surfaced the inconsistency, quantified it, and used it as evidence for a methodological claim. That is honest science.

**Is 4 seeds sufficient at r=16?** For the claim being made, yes, with caveats:

- The core empirical claim is that sigma(CER) >= 0.48%p, which exceeds several adjacent rank-step marginal gains (r=16 -> r=32: 0.24%p; r=32 -> r=64: 0.17%p). Four seeds is enough to establish a conservative lower bound on seed variance. In fact, with only 4 samples the sample standard deviation underestimates the true population sigma in expectation, so the real dispersion is probably larger, not smaller, than reported. This strengthens rather than weakens the claim.
- The 95% CI [8.39, 9.91] computed from n=4 is appropriately wide and does not overclaim precision. The authors use the t-based interval (implicit in the width), which is the correct choice for small n.
- What 4 seeds is NOT sufficient for: (i) estimating the variance with tight confidence (a chi-squared CI on sigma with df=3 is very wide); (ii) detecting small differences BETWEEN rank configurations via paired tests; (iii) distinguishing seed variance from data-ordering variance vs. initialization variance. These are genuine limitations but are not claimed.
- A more rigorous version of this analysis would seed-match across ranks (i.e., run each rank with the same 4 seeds and do a paired comparison). The current design cannot formally test "is r=16 better than r=4" because the r=4 number comes from a single seed. The paper does not quite make this claim -- it says r=16 mean is "statistically indistinguishable" from r=4 at seed 42 -- which is a correct weaker statement.

**Bottom line**: The single-seed concern from Round 2 is substantially resolved for the r=16 configuration and appropriately flagged as an open limitation for the other ranks (now explicitly listed as Limitation #1). The reframing around methodological recommendation is fair and well-supported.

### 1.2 Is "Seed Variance Dominates Rank Differences" a Valid Contribution?

Yes, with appropriate scope. A few observations:

**Strengths of this contribution:**

- It is empirically grounded in the paper's own data, not borrowed from the literature.
- It has concrete numerical teeth: 0.48%p sigma vs. 0.17-0.24%p marginal rank gains at high ranks.
- It reframes the r=8 anomaly coherently without post-hoc storytelling -- the authors admit they cannot distinguish it from variance rather than inventing a capacity-based explanation.
- It has clear practical implications: a practitioner reading a single-seed LoRA rank sweep in the 1k-sample regime should treat the ordering skeptically.
- It is actionable: the authors explicitly recommend multi-seed evaluation as standard practice for LoRA studies on small datasets.

**Caveats the authors should (and partly do) acknowledge:**

- The finding is demonstrated at ONE rank (r=16). Strictly speaking, they have shown sigma(CER) approx 0.48%p at r=16, not that this dispersion is constant across ranks. It is plausible that lower ranks have different variance characteristics (e.g., lower capacity may yield tighter distributions, or vice versa). The paper is careful on this point in Limitation #1, which I appreciate.
- The finding is specific to the low-data regime (1000 samples, 1 epoch). At larger data scales, seed variance likely shrinks. The paper correctly restricts its claim to the low-data regime.
- There is prior literature on seed variance in deep learning (Bouthillier et al. "Accounting for Variance in Machine Learning Benchmarks," 2021; Dodge et al. "Show Your Work," 2019; Reimers and Gurevych on BERT). The authors do not cite this literature. Adding one or two citations would strengthen the methodological positioning and avoid the appearance of reinventing a well-known concern. This is a minor but real weakness.
- The specific claim "multi-seed evaluation is necessary for LoRA rank studies on small datasets" is plausible and supported, but it is one data point on one dataset with one model. Generalization to other languages, model sizes, and data scales is an open question. The paper does not overclaim here.

**Verdict**: Yes, this is a valid contribution. It is modest but honest, empirically grounded, and practically useful. It elevates the paper from "a small rank sweep" to "a small rank sweep plus a methodological cautionary tale," which is a better framing for a workshop venue.

---

## 2. Remaining Methodological Issues

### 2.1 Asymmetric Seed Coverage

The most obvious remaining issue is that only r=16 has multi-seed coverage. The headline numbers for r=4, r=8, r=32, r=64 in Table 2 are all single-seed (seed 42). Given the paper's own finding that sigma approx 0.48%p, the reader should mentally attach error bars of that magnitude to every row of Table 2. The paper acknowledges this clearly in Limitation #1, which is the correct disclosure.

However, a reader skimming only Table 2 and the abstract may still anchor on "r=64 achieves 8.04%" as a precise point estimate. I recommend (but do not require for acceptance):

- A footnote on Table 2 noting that non-r=16 rows are single-seed and should be interpreted with the sigma estimated at r=16.
- Or an asterisk / dagger marker on single-seed rows.

### 2.2 The "Best Configuration" Framing Is Now Slightly Inconsistent

The abstract and Section 5.1 still highlight "r=64 achieves 8.04% CER, a 39% relative improvement." Given the paper's own analysis, this 8.04% is a single-seed point estimate drawn from the same distribution that produced the 8.45% r=16 outlier. If r=64 were also run with 4 seeds, its mean might well overlap the r=16 mean.

The paper partially handles this in Section 5.3 ("the 0.41 percentage points of CER improvement... highlights the importance of evaluating parameter efficiency rather than optimizing for training loss alone") and in the Discussion ("modest gains whose practical significance is within the observed seed variance"). But the abstract's "39% relative improvement" headline is arguably inconsistent with the methodological claim the paper is making. Two options:

- **Keep the headline but add a hedge**: "r=64 achieves 8.04% CER (single seed), a 39% relative improvement over the zero-shot baseline; multi-seed mean at r=16 is 9.15% +/- 0.48% (a 31% relative improvement)."
- **Lead with the multi-seed number**: "Multi-seed LoRA at r=16 achieves 9.15% +/- 0.48% CER, a 31% relative improvement over the 13.18% zero-shot baseline."

I would prefer the second framing since it is more honest to the paper's own methodological thesis, but the first is acceptable. This is a writing issue, not a correctness issue.

### 2.3 Paired Comparisons Would Strengthen the r=16 vs. r=4 Claim

The paper says the r=16 mean (9.15%) is "statistically indistinguishable from our r=4 seed-42 result (9.39%)." Strictly, this is a comparison of a mean to a single point. A proper paired test (run r=4 with the same 4 seeds as r=16) would make this claim rigorous. This is suggested as future work and is acknowledged in Limitation #1. It is acceptable to leave this as-is for the current submission, but a seed-matched r=4 run would be the single highest-value addition for a follow-up.

### 2.4 The alpha = 2r Confound Still Stands

My Round-2 comment about alpha scaling with rank (confounding rank capacity with effective learning rate) was not addressed in the revision. It is a minor point but remains a genuine confound. A sentence in the Method or Discussion section would suffice. Not a blocker.

### 2.5 Missing Citations on Seed Variance

As noted in 1.2, the paper should cite prior work on seed variance in deep learning / ASR. Suggested additions:

- Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks," MLSys 2021.
- Dodge et al., "Show Your Work: Improved Reporting of Experimental Results," EMNLP 2019.
- Reimers and Gurevych, "Reporting Score Distributions Makes a Difference," EMNLP 2017.

This grounds the methodological recommendation in an existing conversation and avoids the appearance of rediscovery.

### 2.6 Latency Anomaly Still Unresolved

The non-monotonic latency pattern in Table 2 is still unexplained and is still only flagged in limitations. As suggested in Round 2, adding a footnote to the Latency column of Table 2 would be a minimal fix.

### 2.7 Minor Items Still Standing

- Code/data availability: still not mentioned.
- Title still says "Korean Speech Recognition" without the "read speech" qualification.
- Comparison to prior work remains qualitative rather than citing specific numbers on zeroth_korean.
- Section 3.2 still says "three rank configurations (r in {4, 16, 64})" but the experiments now cover five. This is a stale sentence that should be updated to match Section 5.1.

---

## 3. Assessment of the Round-3 Contribution Set

The paper now presents three complementary contributions:

1. **Rank scaling empirics**: 5 ranks, clear diminishing returns past r=16. Useful reference.
2. **Parameter efficiency analysis**: Params per %p CER reduction, 4x cost increase from r=4 to r=64. Useful practical guidance.
3. **Multi-seed variance characterization**: sigma(CER) approx 0.48%p at r=16, with the specific observation that this exceeds marginal rank gains. Methodological contribution.

Contribution 3 is the most interesting. It is the kind of "negative result plus actionable recommendation" that is often missing from the literature because it does not make authors look good -- but this team handled it with unusual honesty, identifying their own headline number as an outlier. That deserves credit.

Collectively, the three contributions justify a workshop paper firmly. For a main-track venue (ICASSP, Interspeech), the scope is still narrow (one dataset, one model size, one language, one PEFT method), but the methodological angle strengthens the case.

---

## 4. Recommendation

### Round-3 Decision: **Accept (workshop)** / **Weak Accept (main track)**

**Confidence**: 4 (High)

**Justification**:

- Round-1 integrity issues (fabricated data, unimplemented method, duplicated sections): fully resolved in Round 2 and unchanged in Round 3.
- Round-2 single-seed concern: substantially resolved. The authors did not just add multi-seed runs; they surfaced an uncomfortable finding (their own headline was an outlier), reframed the paper around it, and produced a methodological contribution. This is the right response.
- Remaining issues (asymmetric seed coverage, alpha=2r confound, missing citations, stale text in Section 3.2, latency footnote) are all minor and addressable with small edits. None are blockers.
- The paper is honest, internally consistent, appropriately scoped, and practically useful. It is a textbook example of a revision trajectory done well.

**For a workshop venue** (efficient ML, low-resource ASR, on-device ML): I recommend **Accept**. The empirical rigor and methodological honesty exceed typical workshop standards.

**For a main-track venue** (ICASSP, Interspeech): I recommend **Weak Accept**. The experimental scope remains narrow (single dataset, single model size, single language, single PEFT method), but the methodological contribution on seed variance partially compensates. Main-track reviewers less focused on methodology may find the contribution thin; main-track reviewers who value honest empirical work will find it refreshing.

### Required changes for camera-ready (all minor):

1. Fix stale Section 3.2 sentence ("three rank configurations") to match actual 5-rank sweep.
2. Add a footnote to Table 2 noting non-r=16 rows are single-seed.
3. Add a footnote to the Latency column about single-pass measurement unreliability.
4. Cite at least one prior work on deep learning seed variance (Bouthillier, Dodge, or Reimers/Gurevych).
5. Add one sentence on the alpha=2r confound in Method or Discussion.
6. State code/data availability intent.
7. Consider reframing the abstract's "39% relative improvement" around the multi-seed mean rather than the single-seed r=64 outlier, or add a hedge.

### Recommended (not required) for future work:

1. Seed-match r=4 (and ideally all ranks) to enable proper paired comparisons.
2. Full multi-seed sweep across all 5 ranks.
3. Test whether the sigma approx 0.48%p finding generalizes to Whisper Base/Medium or to other datasets.
4. Vary alpha independently of r to decouple capacity from effective update scale.

---

## 5. Closing Note

I want to explicitly commend the authors for how this revision was handled. Identifying one's own published headline number as a lower-tail outlier and restructuring the paper around that uncomfortable fact is rare and valuable. Many authors in this position would have quietly added a seed-averaged number that happened to come out favorably, or buried the variance finding in an appendix. These authors foregrounded it. That is the behavior the community should reward.

The trajectory from Round 1 (fabricated data, reject) to Round 3 (honest methodological contribution, accept) represents one of the more substantive and honest revision sequences I have reviewed. I am confident in recommending acceptance.
