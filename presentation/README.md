# Results presentation

The presentation is being updated. The [presentation draft](PRESENTATION_DRAFT.md) contains the proposed narrative, essential text and visual recommendations for each slide, precise sources, reusable charts and a ready-to-use Claude Design prompt.

The draft recommends restructuring the story around 10 main slides with optional technical appendices. It opens with the survey problem and data, then explains preprocessing, NumPy boosting, historical comparisons, evaluation, challenge feedback and limitations. The slide count is a guide rather than a requirement.

The previous [PDF](RESULTS_PRESENTATION.pdf) and [editable PowerPoint](RESULTS_PRESENTATION.pptx) remain available as the 14 October 2026 version: 16 slides, including 14 main slides and two appendices. They have not been replaced in this documentation update. Use the revised draft and current documentation as the handoff for the new design.

The selected pipeline records author-reported **AIcrowd F1 0.455 and accuracy 0.882**. Full-training OOF F1 **0.443882** describes threshold calibration; historical nested F1 **0.442155** belongs to the earlier Phase 14 pipeline. No completed nested estimate exists for the exact final combination. The author-reported **3rd place on 14 October 2026** is a dated snapshot, not a final placing or an independently verified rank. These distinctions and the post-event limitation of `HAREHAB1` must remain visible in the new presentation.

The source comparison was made against public `main` at [d6cbe39a669c61d9f3bbf1da1ac0dc0034c4be94](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/commit/d6cbe39a669c61d9f3bbf1da1ac0dc0034c4be94) on **15 October 2026**. The [release evidence](../evidence/RELEASE_20261014.json) and its presentation fingerprints remain the original dated record. No new training was performed for this update.

The [results guide](../docs/RESULTS.md), [runnable project](../project/README.md), [selected configuration](../project/configs/final_model.json) and [submission record](../project/results/eda/final_combined18_24_submission.json) provide the current methodological context.

**Author:** Antonio Arbizzani Tonelli. **Context:** EPFL Machine Learning CS-433.
