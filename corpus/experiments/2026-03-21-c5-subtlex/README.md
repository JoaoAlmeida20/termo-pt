# 2026-03-21 · SUBTLEX-PT extraction (c5)

The original word-list extraction. **Promoted**: the canonical lists at
`corpus/words-*.txt` and the ones the app ships (`src/data/*.txt`) are byte-identical
copies of the two files in this folder — production still runs on this run.

## Run

- Date: 2026-03-21 (~18:50), under WSL — output has LF endings.
- Committed to git on 2026-04-03 (`630fc2b`, "Initial implementation…").
- No folder existed at the time: the script (then SUBTLEX-only, at `corpus/`)
  wrote directly into the corpus base. This folder was reconstructed 2026-10-17
  during the corpus reorganization; `extract_words.py` is the script exactly as
  committed in `630fc2b`.

## Input

- `subtlex_pt.xlsx` — SUBTLEX-PT (Soares et al.), sheet `SUBTLEX-PT`.
  Spreadsheet authored 2014 (creator "Ana Paula Soares"), obtained 2026-03-21
  from CLUL (www.clul.org). Git-ignored; re-download if missing.

## Reproduce

```
python extract_words.py 5     # run FROM this folder
```

Reads `subtlex_pt.xlsx` from the cwd and writes `words-*.txt` to the cwd,
overwriting the lists kept here (they match the committed version, so this is
safe — `git diff` will show if a rerun changes anything). Requires pandas + openpyxl.

## Output

| file | words | notes |
|---|---|---|
| `words-answer.txt` | 3,641 | excludes verb-only non-infinitives |
| `words-valid.txt` | 5,969 | all alphabetic c5 wordforms |
