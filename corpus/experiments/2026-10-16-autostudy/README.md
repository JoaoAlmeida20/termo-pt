# Word-list experiment (2026-10)

Self-contained experiment for better European-Portuguese (pt-PT) 5-letter lists:
inputs, sources and outputs all live inside this folder; it does
**not** touch `corpus/words-*.txt` or `src/data/*.txt`.

Researched autonomously by agent; technical report of the research, experiments and results is `REPORT.html` (open in a browser).

## Outputs (`output/`)

| file | what |
|---|---|
| `words-answer.txt` | **recommended answers** (1,692): rules + LLM review |
| `words-valid.txt` | **recommended valid guesses** (6,973): one spelling per accent-stripped key |
| `variants/no-fem/` | same, without feminine forms (obesa, tonta…) — 1,513 answers |
| `variants/auto/` | rules only, no LLM review — 1,223 answers |
| `variants/auto-strict/` | rules only, familiarity ≥ 3.5 — 837 answers |
| `answers-scored.tsv` | answers ranked by EP familiarity, with shape and BR-lean flag |
| `metrics.json`, `blind_ab.json`, `eval_br.txt` | evaluation results |

Same format as the canonical lists (one word per line, UTF-8, lowercase, accented),
so promoting is a copy: `cp output/words-*.txt ../../` and `src/data/`.

## Pipeline

```
scripts/fetch_sources.sh      download sources into sources/ (git-ignored, ~600 MB)
scripts/run_all.sh            rebuild everything (~1 min)
  01_local_corpora.py         inputs/*.xlsx (SUBTLEX-PT + ESCOLEX) -> work/*.tsv
  hunspell_expand.py          unmunch Hunspell pt_PT / pt_BR (with Natura morphology)
  05_wiktionary.py            kaikki.org Wiktionary -> per-word tags
  10_features.py              join all sources -> work/features_c5.tsv
  30_review_merge.py          merge LLM review batches -> eval/llm_review.tsv
  20_select.py                rules -> output/
  eval_br.py                  BR detector on gold + LanguageTool held-out pairs
  40_evaluate.py              coverage / leakage / collisions -> metrics.json
  50_blind_score.py           blind A/B judgement -> blind_ab.json
tests/app_compat.test.ts      lists vs the app's own accent logic (npx vitest run corpus/experiments/2026-10-16-autostudy/tests)
```

Requirements: Python 3.11+, `pandas`+`openpyxl` (step 01 only), `spylls==0.1.7`.
Scripts run with `python -P` (downloaded data is treated as untrusted).

## Sources

SUBTLEX-PT (+ its P-PAL column) · ESCOLEX (both in `inputs/`, git-ignored) · LibreOffice/Natura Hunspell pt_PT (AO90)
and VERO pt_BR · Natura full wordlists (AO / pre-AO) · OpenSubtitles 2018 pt vs pt_br
(hermitdave) · Linguateca AC/DC totalpt vs totalbr · CLUL CORLEX · Leipzig
newscrawl pt vs br, web pt · kaikki.org English-Wiktionary Portuguese ·
LanguageTool `dialect_alternations.txt` (evaluation only).

## Evaluation data (`eval/`)

- `gold_br.txt`, `gold_ep.txt`, `gold_neutral.txt` — small hand-made gold sets
- `llm_batches/` — 10 × ~407-word LLM review batches (+ 25 cross-batch duplicates
  each for self-consistency) and `out_10.tsv` (4 words reviewed by hand)
- `llm_review.tsv` — merged verdicts (keep/obscure/br/foreign/vulgar/inflected/proper/error + familiarity 1-5)
- `blind/` — blind A/B sample (523 words from 3 lists, unlabelled) and two judges' verdicts
