# Morpheus
Estimates whether text is human-written (0) or AI-generated (1). **Output is a likelihood estimate, not proof of authorship, and must not be used as a plagiarism or cheating detector.**

## Run the baseline demo (Python 3.11+, from project root)
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-baseline.txt
python app.py
```

## Train and evaluate (full development environment)
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.download_data          # public HC3 dataset; verify its license first
python -m src.validate_data && python -m src.clean_data && python -m src.split_data
python -m src.train_baseline
python -m src.train_transformer --max_train_samples 2000   # CPU quick run; omit for full
python -m src.evaluate && python app.py
pytest -q
```
Offline smoke test: `python -m src.make_sample`, then pass `--input data/raw/sample.csv --min_words 5` to validate/clean (synthetic; metrics are meaningless).
Landing page + legal pages: open `site/index.html` (fill every [PLACEHOLDER]; have a lawyer review).

## Landing page
- The landing page is in `site/` and uses the Morpheus ivory/yellow design system.
- Lenis is bundled locally as `site/lenis.min.js` for optional smooth scrolling, with reduced-motion support.
- Basement Studio is used as a visual direction reference; Watermelon UI is used only as inspiration for modular, accessible component patterns. The project remains plain HTML/CSS/JavaScript.

### What I built with Lenis

Lenis is used as the landing page's scroll engine. In `site/app.js`, the page creates one Lenis instance, advances it through `requestAnimationFrame`, and uses it for in-page anchor navigation. This gives the Morpheus landing page a slower, controlled scroll feel without replacing the semantic HTML structure or changing the detector's Python model code.

The library is stored locally at `site/lenis.min.js` instead of being loaded from a runtime CDN. The page checks `prefers-reduced-motion`; when a visitor has reduced motion enabled, Lenis is not started and native scrolling is preserved. CSS animations and reveal transitions are disabled in the same mode.

Lenis is intentionally limited to scroll behavior. The visual identity comes from the custom Morpheus CSS system: ivory surfaces, charcoal type, yellow signal accents, self-hosted fonts, orbital hero artwork, scroll progress, and small intersection-observer reveals. This keeps the interaction layer separate from the model layer and makes the page easier to maintain.

### Project summary

Morpheus is an experimental NLP classifier that estimates whether writing contains patterns associated with AI-generated text. The baseline model uses TF-IDF and Logistic Regression; the result is a probability estimate, not proof of authorship. The project includes data validation, cleaning, group-aware splitting, evaluation reports, a Gradio detector interface, and a custom landing page.

## Decisions
- Cleaning keeps case/punctuation/paragraphs; near-duplicates (TF-IDF cosine ≥ 0.9) are clustered, and clusters plus shared `group_id` never cross splits. PII-looking rows are flagged to `data/interim/flagged.csv` and excluded.
- Split: StratifiedGroupKFold, seed 42, ≈70/15/15. TF-IDF is fit inside the training pipeline only.
- Transformer: distilbert-base-uncased, max 256 tokens, early stopping on val F1.
- Slices with <30 rows report "insufficient data". "Unseen generator/source" and "lightly edited AI" slices need data with those tags; HC3 has one generator (ChatGPT), so they are not measurable until you add more.

## Limitations
Distribution shift (new LLMs, domains), paraphrasing/translation evading detection, false positives on formal or non-native writing, and single-generator training data. Check class balance in `reports/validation_report.json`.
