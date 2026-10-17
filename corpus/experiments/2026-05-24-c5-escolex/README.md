# 2026-05-24 · ESCOLEX extraction (c5)

Second research iteration: rebuild the lists from ESCOLEX (school-leavers'
vocabulary) instead of SUBTLEX-PT. **Not promoted** — the canonical lists are
still the 2026-03-21 SUBTLEX run; these lists were only ever archived.

## Run

- Date: 2026-05-24. Timeline from file metadata: `ESCOLEX.xlsx` downloaded
  12:26, reference PDF fetched 12:37, extraction script refactored to a
  multi-corpus form 14:55, lists produced ~15:06.
- Executed under native Windows Python (output had CRLF). During the 2026-10-17
  corpus reorganization the lists were normalized to LF and the script below
  forces `newline='\n'`, so reruns stay LF everywhere.

## Inputs

- `ESCOLEX.xlsx` — sheet `G1-G6` (internal metadata: created 2014-02-20,
  revision 33). From CLUL (www.clul.org). Git-ignored.
- `Soares_et_al.__in_press_ESCOLEX.pdf` — Soares et al., *The European
  Portuguese adaptation of ANEW* (2013), read 2026-05-30. Background paper for
  both ESCOLEX and SUBTLEX-PT. Git-ignored.

## Reproduce

```
python extract_words.py 5     # run FROM this folder
```

The script here is the ESCOLEX-only distillation of the last uncommitted
multi-corpus `corpus/extract_words.py` (generic `corpus/extract_words.py` was
retired in the reorg; its SUBTLEX ancestor lives in `../2026-03-21-c5-subtlex/`).
Writes `words-*.txt` into this folder. Requires pandas + openpyxl.

## Output

| file | words | notes |
|---|---|---|
| `words-answer.txt` | 2,468 | 2,372 of them are also in the canonical answers (of 3,641) |
| `words-valid.txt` | 3,460 | much stricter than canonical (5,969) |
