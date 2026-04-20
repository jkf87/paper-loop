# Review 3 (Round 3): Writing and Presentation

**Paper**: LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study on Consumer Hardware

**Reviewer Role**: Writing, presentation, and claims expert

**Review History**:
- Round 1: Weak Reject (duplicated sections, overclaims, missing data)
- Round 2: Weak Accept (clean rewrite, minor issues remaining)
- Round 3: **Accept** (see below)

**Confidence**: 4/5

---

## Summary of Changes Since Round 2

The authors have addressed essentially every remaining issue from the previous round and added a substantial new experiment:

1. **Abstract rewritten** to foreground the multi-seed variance finding as the methodological headline.
2. **Contributions expanded from 3 to 4 items**, with a new "multi-seed variance characterization" bullet.
3. **New Section 5.3 "Multi-Seed Evaluation at r=16"** with Table 4 (four seeds: 42, 123, 456, 789; mean 9.15%, std 0.48%p, 95% CI [8.39, 9.91]) and a dedicated figure.
4. **Main results table extended** from 3 to 5 LoRA ranks (r=4, 8, 16, 32, 64), exposing the non-monotonic r=4 -> r=8 step.
5. **Efficiency table now shows negative marginal** (-0.88 %p for r=4 -> r=8), explicitly flagging non-monotonicity as motivation for multi-seed analysis.
6. **Discussion "Practical implications"** rewritten to ground recommendations in the multi-seed mean (9.15%), not the seed-42 outlier (8.45%).
7. **Conclusion reframed** as a methodological contribution about multi-seed necessity in low-data LoRA sweeps.
8. **Limitations item 1** changed from "single runs" to "partial multi-seed coverage," with specific honest language about single-seed numbers at the other ranks being point estimates.
9. **Figure 1 (rank scaling) now present**, plus new Figure 3 (multi-seed dispersion). Three figures total, all with \includegraphics environments.

---

## Re-Evaluation Against Round 2 Outstanding Issues

| Round 2 issue | Round 3 status |
|---|---|
| Figure 1 missing | FIXED. `charts/fig_rank_scaling.png` now embedded at line 150. |
| Single-seed limitation | SUBSTANTIALLY ADDRESSED. Four-seed run at r=16 adds real variance estimate; Limitations now honestly frames coverage as partial. |
| Uncited comparison claims in Discussion | NOT ADDRESSED. The "consistent with reported performance" and "approaches Whisper Medium or Large" statements in Section 6 still lack citations. |
| Latency anomaly in Table 1 should have a footnote | NOT ADDRESSED. Table 1 caption still reads only "Best values in bold. All LoRA runs use seed 42 unless noted." The non-monotonic latency column (1.35 -> 1.06 -> 1.05 -> 1.86 -> 1.05 -> 1.28) is discussed only in Limitations item 7. |

Two of the four Round 2 minor items remain. Neither is severe, but they are the easiest wins in a final camera-ready pass.

---

## Evaluation Criteria

### 1. Writing quality: maintained or improved?

**Improved.** The multi-seed section is the best-written part of the paper. Key sentences like *"the original seed-42 r=16 result (8.45% CER) is a lower-tail outlier"* and the explicit framing that *"single-seed rank sweeps can produce misleading conclusions about the ordering of LoRA configurations"* are crisp, falsifiable, and honest. The prose remains direct throughout. No jargon inflation returns. The transitions between the main table non-monotonicity, the efficiency table negative marginal, and the multi-seed analysis now form a clean narrative arc (observe anomaly -> quantify variance -> reinterpret).

Minor copy issue: in Section 3.2 line 75, the text still says "We evaluate three rank configurations (r in {4, 16, 64})" -- this is a stale sentence from the earlier draft that contradicts the expanded five-rank sweep reported in Section 5. This should be updated to "five rank configurations (r in {4, 8, 16, 32, 64})" before camera-ready.

Minor units issue: Discussion line 226 writes "9.15%p CER" and "8.21%p" -- the "%p" suffix is for percentage-point differences, not absolute CER. These should be plain "%".

### 2. Does the multi-seed framing strengthen or weaken the narrative?

**Strengthens substantially.** This is now the paper's most defensible and most novel contribution. Rank sweeps without seed variance are a known but under-reported problem in the LoRA literature, and producing a concrete case where the std (0.48 %p) exceeds four of the five adjacent marginal steps is a useful empirical data point for the community. Crucially, the authors do not oversell this: they present it as a methodological cautionary finding, not a new method.

The reframing also retroactively justifies the r=4 -> r=8 non-monotonicity (previously an embarrassment) as evidence for the central thesis. The paper now has an internally coherent story it did not have in Round 2.

Narrative risk: the paper now makes two somewhat competing claims -- (a) "diminishing returns beyond r=16" and (b) "differences between ranks are within seed noise." Statement (a) is in the abstract, contributions, and conclusion. Statement (b), if taken strictly, undermines statement (a), because if the r=16 mean (9.15%) is statistically indistinguishable from r=4 seed-42 (9.39%) and worse than r=32 seed-42 (8.21%), then diminishing returns "past r=16" is no longer clearly demonstrated on the available data. The paper mostly navigates this tension honestly in Section 5.3, but the Introduction contribution bullet (line 40) still asserts "marginal CER improvement becomes negligible beyond r=16" as a factual finding when the multi-seed data arguably shows we do not yet know this at the r=16 -> r=32 boundary. Softening this bullet to "marginal single-seed CER improvement" or "within-noise-level improvement" would remove the internal tension.

### 3. Does the paper overclaim anywhere?

Mostly no. Specific spots to check:

- **Abstract**: "39% relative improvement" is a single-seed number (13.18% -> 8.04%). Given the paper's own argument that r=16 at seed 42 is a lower-tail outlier, the r=64 seed-42 number is also a single-seed point estimate with unknown variance. The headline is still technically correct but is in tension with the paper's methodological message. A single qualifier ("at seed 42") in the abstract would fully align the headline with the multi-seed finding. This is a soft overclaim.

- **Contribution 1** (line 40): "marginal CER improvement becomes negligible beyond r=16" -- as noted above, this is more confident than the multi-seed evidence supports. Soft overclaim.

- **Contribution 3** (line 42): "significant CER reduction (13.18% -> ~9% mean at r=16)" -- this is now properly hedged with "mean." Good.

- **Section 5.3 claim of statistical indistinguishability** (line 215): "the mean across four seeds (9.15%) is statistically indistinguishable from our r=4 seed-42 result (9.39%)" -- this is stated without a formal test. With n=4 and std 0.48, a one-sample t-test of 9.39 against the four-seed distribution (t = (9.39 - 9.15) / (0.48/2) = 1.0, p ~ 0.39) does support indistinguishability, so the claim is defensible, but the paper should either cite the test or soften to "within one standard deviation." Minor.

- **Conclusion** (line 254): "showing that single-seed rank sweeps in low-data regimes can produce misleading orderings" -- correctly hedged with "can." Good.

- **Discussion "Comparison to prior work"** (line 232): still contains the two uncited comparison claims flagged in Round 2. These are soft overclaims because the reader cannot verify them.

No hard overclaims. Two soft ones and one internal-consistency issue between the methodological message and the diminishing-returns framing.

### 4. Is the title still accurate?

**Yes, and arguably more accurate than in Round 2.** The title "LoRA Rank Scaling for On-Device Korean ASR: An Empirical Study" promises a rank scaling empirical study on consumer hardware. The paper now delivers exactly that, plus a multi-seed variance characterization at one rank. The multi-seed work is consistent with the "empirical study" framing and does not require a title change.

An alternative title such as "LoRA Rank Scaling for On-Device Korean ASR: On the Necessity of Multi-Seed Evaluation" would foreground the methodological contribution, but the current title is honest and does not overpromise. I do not recommend a change.

### 5. Structural and presentation check

- Section 3.2 "Rank Scaling Protocol" still says "three rank configurations" -- stale text, must be updated to five.
- Table 1 has no footnote on latency despite the Round 2 recommendation.
- The "Training Loss vs. Test Performance" subsection (5.4) still uses the seed-42 r=16 number (4.67 train loss, single run), which is fine, but the 0.41 %p test improvement figure should arguably now reference that this is within-noise given std 0.48 %p. Minor.
- Figures: three figures, all referenced, all with captions. Good.
- Tables: four tables (hyperparams, main results, efficiency, multi-seed), all complete. Good.
- Limitations list is now 7 items; item 1 ("partial multi-seed coverage") is particularly well-phrased and gives reviewers exactly the caveats they would otherwise write themselves.

---

## Remaining Minor Issues for Camera-Ready

1. **Stale "three rank configurations" in Section 3.2 line 75** -- update to five. (Must fix.)
2. **Latency footnote on Table 1** -- add a one-line note referencing Limitations item 7. (Should fix.)
3. **Uncited comparison claims in Section 6** -- either add citations for the "consistent with reported performance" and "Whisper Medium/Large" claims or soften to "in the range reported by informal benchmarks." (Should fix.)
4. **Contribution 1 wording** -- soften "negligible beyond r=16" to acknowledge the multi-seed tension. (Should fix.)
5. **Abstract qualifier** -- adding "(seed 42)" after the 39% headline would fully align the abstract with the methodological message. (Nice to have.)
6. **%p vs. % units in Discussion line 226** -- two typos. (Must fix, trivial.)
7. **Statistical indistinguishability claim in Section 5.3** -- add a one-line t-test result or soften to "within one standard deviation." (Nice to have.)

None of these block acceptance.

---

## Writing Quality Assessment

The prose is clear, direct, and technically appropriate. The new Section 5.3 is genuinely well-written: it introduces the experiment, reports raw numbers, states summary statistics with a confidence interval, and draws two carefully-bounded conclusions. The Limitations section remains unusually honest for the genre. The abstract is tighter than Round 2 despite carrying more content. The paper has moved from "clean empirical report" (Round 2) to "clean empirical report with a genuine methodological takeaway" (Round 3), which is a meaningful upgrade.

---

## Final Assessment

The authors responded seriously to Round 2. They did the work that reviewers wished had been done (multi-seed at r=16), extended the rank sweep from 3 to 5 configurations, produced the missing figure, and most importantly found the intellectual honesty to reinterpret their own headline result (the 8.45% r=16 number) as a lower-tail outlier. The paper is now internally consistent in its methodology message, has complete data, and makes no hard overclaims.

The remaining issues are cosmetic and copy-editing level (stale sentence about "three configurations," two unit typos, missing latency footnote, two uncited comparison claims, a slightly over-confident contribution bullet). None are evidentiary. The contribution is modest but the execution is honest and the methodological finding about seed variance exceeding rank-step marginals is a genuinely useful data point for the PEFT-for-speech community.

This paper has now earned a clean Accept for a workshop or short empirical track. It would still be a Weak Accept at a top-tier main conference due to the narrow scope (one model, one dataset, one hardware platform, one rank with full multi-seed coverage), but within the empirical-study-on-consumer-hardware genre, the paper does everything right.

**Score**: **Accept**
**Confidence**: 4/5

I am confident in this assessment. The paper has improved monotonically across three rounds, the authors have demonstrated they act on reviewer feedback substantively (not cosmetically), and the remaining issues are all addressable in a single camera-ready pass without any new experiments.
