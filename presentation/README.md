# Results presentation handoff

This folder specifies the **14 October 2026 completed portfolio release**. Selected pipeline: `combined18_24_l2_1`; author-reported AIcrowd F1 **0.455**, accuracy **0.882**, and current rank **3** on **14 October 2026**. The finished presentation will be created in Claude Design and added here after export.

## Create the deck in Claude Design

1. Use the latest local `CLAUDE_DESIGN_INPUT.zip` in this folder. It packages the guide, prompt, results documentation, charts and evidence for the release. The ZIP is a local handoff bundle excluded from Git.
2. Upload it to Claude Design. Open [CLAUDE_DESIGN_PROMPT.md](CLAUDE_DESIGN_PROMPT.md), copy the prompt between the separators and paste it into the design request.
3. Follow [CLAUDE_DESIGN_BRIEF.md](CLAUDE_DESIGN_BRIEF.md): 16 main slides and 3 appendices; editable 16:9 PPTX, matching PDF and slide PNG previews, all in English.
4. Download exports as `RESULTS_PRESENTATION.pptx` and `RESULTS_PRESENTATION.pdf`. Review each preview before publication.

If using files downloaded from GitHub, upload the guide and prompt, `docs/RESULTS.md`, `docs/CODE_REVIEW.md`, `evidence/RELEASE_20261014.json`, `evidence/METRICS.json`, `evidence/VERIFICATION.json`, `evidence/SELECTED_REPLAY_20261014.json`, the `evidence/aicrowd/` records, both `assets/chart_data/` CSVs, `project/configs/final_model.json`, `project/configs/experiments/combined18_24_preprocessing.json`, and technical notes referenced by the guide. Markdown is the authoritative guide; its companion PDF is a reading copy of the specification, not the slide deck.

## Check the exported presentation

- Final model is combined diet + restricted imputation using the preserved Phase 14 booster. Standalone Phase 14 is the historical reference.
- Challenge F1 **0.455** / accuracy **0.882** and rank **3**, dated **14 October 2026**, show their reported provenance.
- Historical nested F1 **0.442155**, selected OOF calibration F1 **0.443882** and challenge F1 **0.455** have separate labels. No combined held-out result is invented.
- The post-event `HAREHAB1` limitation is visible. Prediction counts are not called a confusion matrix.
- Tables and charts are readable after PDF export, links work and text is not clipped.

## Add the finished deck to GitHub

Place both exports in this `presentation/` folder, then run from the **repository root**:

```bash
git add presentation/RESULTS_PRESENTATION.pptx presentation/RESULTS_PRESENTATION.pdf
git commit -m "Add results presentation for the 14 October 2026 portfolio release"
git push
```

Add root README links after both files exist. Keep guide, prompt and evidence beside the deck so later releases can update it consistently. Review PPTX and PDF together after revisions; update dates and results when a newer completed result is adopted.

Official challenge data, model checkpoints, row-level predictions and the private academic submission report remain outside Git and are not deck inputs.
