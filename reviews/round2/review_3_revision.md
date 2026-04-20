# Review 3 (Revision): Writing and Presentation

**Paper**: LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study on Consumer Hardware

**Reviewer Role**: Writing, presentation, and claims expert

**Previous Score**: Weak Reject

**Revised Score**: Weak Accept

**Confidence**: 4/5

---

## Summary of Changes

The paper has been completely rewritten. The revised version is a focused empirical study of LoRA rank scaling (r in {4, 16, 64}) applied to Whisper Small for Korean ASR on Apple M4 hardware. Every major issue from the prior review has been addressed: duplicated sections are eliminated, the title and framing are honest, overclaimed contributions have been removed, hyperparameters are fully specified, and the tables contain real, complete data. The paper is now a clean, short (approximately 5 pages of content), well-structured empirical report.

---

## Assessment of Revisions

### Issues Resolved

1. **Structure (Critical -- FIXED)**: The duplicated sections, broken numbering, and concatenated-draft artifacts are entirely gone. The paper now follows a clean single-pass structure: Introduction, Related Work, Method, Experiments, Results, Discussion, Limitations, Conclusion. Each section appears exactly once.

2. **Title and Framing (Critical -- FIXED)**: The title "LoRA Rank Scaling for On-Device Korean Speech Recognition: An Empirical Study" accurately describes what the paper delivers. The inflated "Jamo-LoRA" branding, "AutoResearch loop," "phonetic-semantic inversion," and "meta-optimization agent" terminology have all been removed. The paper no longer claims novelty it does not possess.

3. **Claims vs. Evidence (Critical -- FIXED)**: The abstract now reports the correct headline number (39% relative CER improvement, 13.18% to 8.04%) and clearly identifies r=16 as the recommended trade-off. There is no longer a contradiction between the abstract result and the paper's recommendation. The "50% improvement" and "statistically significant correlation" overclaims are gone. The contributions are stated as empirical findings, not methodological innovations.

4. **Tables (Critical -- FIXED)**: Table 1 (main results) now contains complete data for all four configurations (baseline + three LoRA ranks) with no missing values. Table 2 (efficiency analysis) is new and well-constructed, showing marginal CER improvement per rank step alongside parameter cost. Both tables are informative and internally consistent.

5. **Missing Hyperparameters (Major -- FIXED)**: Table 3 (hyperparameters) is comprehensive: optimizer, learning rate, batch size, gradient accumulation, epochs, warmup steps, LoRA alpha, dropout, target modules, training samples, and random seed are all specified. This is a model of good experimental reporting.

6. **Related Work (Major -- FIXED)**: The related work now covers QLoRA (Dettmers et al., 2023), KsponSpeech (Bang et al., 2020), and positions the zeroth_korean dataset in context. The coverage is adequate for the scope of the paper.

7. **Figures (Major -- PARTIALLY FIXED)**: The duplicate figures (Fig 6/7, repeated component analysis) are eliminated. However, the paper references Figure 1 (rank_scaling) in Section 5.2 but there is no \includegraphics command or figure environment in the source. This figure is referenced but not actually included.

8. **Vague Method Descriptions (Major -- FIXED)**: The composite loss L_sem and the unspecified "Jamo tokenizer augmentation" are both removed. The method section now describes standard LoRA applied to Whisper, which is exactly what the experiments use. There is no gap between described method and actual implementation.

---

### Remaining Issues

#### Minor Issues

1. **Missing Figure**: Figure 1 (referenced as "fig:rank_scaling" in Section 5.2) is not included in the LaTeX source. A rank scaling plot showing CER vs. trainable parameters across the three configurations would strengthen the paper and should be added before camera-ready.

2. **Single Seed**: The authors now honestly acknowledge this in Limitations (item 1), which is the right approach. However, the 0.41 percentage point difference between r=16 and r=64 is small enough that it could easily be within noise. The paper would benefit from noting explicitly in Section 5.2 that this difference may not be statistically significant, rather than relegating this caveat solely to the Limitations section.

3. **Latency Anomaly**: The non-monotonic latency pattern (r=4: 1.06s < baseline: 1.35s, then r=16: 1.86s, r=64: 1.28s) is acknowledged in Limitations (item 7) as likely MPS backend variability. This is honest, but the latency column in Table 1 may mislead readers who do not read the limitations carefully. Consider adding a footnote to Table 1 noting this variability.

4. **Comparison to Prior Work**: Section 6 states the zero-shot CER is "consistent with reported performance" and that the best LoRA result "approaches the performance typically associated with Whisper Medium or Large variants on Korean." Both claims lack citations. Adding specific numbers from published work would ground these comparisons.

5. **Citation Format**: The source uses \citep with natbib and plainnat style, which is correct. However, the actual .bib file was not reviewed, so citation rendering quality (e.g., whether [zeroth2018] renders properly) cannot be verified.

6. **No Qualitative Examples**: The paper would benefit from a small table showing 2-3 example transcriptions at each rank versus the reference, particularly for cases involving Korean phonological phenomena (consonant assimilation, syllable-final neutralization). This would make the CER improvements more interpretable.

---

## Writing Quality

The prose is clear, concise, and appropriately technical. The paper avoids the jargon inflation of the previous version. Sentences are direct. Claims are properly hedged ("suggests," "these findings indicate"). The abstract is well-constructed: it states the problem, method, dataset, key result, and practical recommendation in a logical sequence. The Limitations section is unusually thorough and honest for the genre, listing seven specific caveats. This transparency strengthens rather than weakens the paper.

---

## Structural Assessment

The structure is clean and standard:
- Abstract: Clear, accurate, no overclaims
- Section 1 (Introduction): Motivates the problem, states three contributions that match what the paper delivers
- Section 2 (Related Work): Adequate coverage for an empirical study
- Section 3 (Method): Clean description of standard LoRA, rank scaling protocol, full hyperparameter table
- Section 4 (Experiments): Dataset, metrics, hardware -- all specified
- Section 5 (Results): Main results table, efficiency analysis, training loss discussion
- Section 6 (Discussion): Practical implications, data efficiency, comparison to prior work
- Section 7 (Limitations): Seven specific, honest limitations
- Section 8 (Conclusion): Concise, forward-looking

No section is duplicated. No section is misplaced. The information density is good throughout.

---

## Final Assessment

This is a substantially different paper from the one previously reviewed. The authors have taken the feedback seriously: the paper is now honest about its scope (an empirical study, not a novel method), the data is complete, the structure is clean, and the claims match the evidence. The contribution is modest -- a rank scaling study on one model, one dataset, one hardware platform, single seed -- but the paper is transparent about this, and the practical finding (r=16 is the sweet spot for on-device Korean ASR) is useful.

The remaining issues are minor: a missing figure, a few uncited comparison claims, and the inherent limitation of single-seed experiments. None of these prevent publication, though addressing them would improve the final version.

**Score**: Weak Accept
**Confidence**: 4/5

The paper meets the bar for a workshop or short empirical contribution. It is well-written, honest, and contains complete data. The contribution is incremental but clearly presented. I would recommend acceptance conditional on including the referenced but missing rank scaling figure and adding specific citations for the comparison claims in Section 6.
