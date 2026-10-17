# corpus

Word lists that feed the game. The app bundles `src/data/answers.txt` and
`src/data/valid.txt` at build time (`?raw` imports in `src/data/words.ts`);
these are the two lists below, copied verbatim.

## Canonical lists (this folder)

- `words-answer.txt` (3,641) — daily words, picked per date by a hashed PRNG.
- `words-valid.txt` (5,969) — accepted guesses (accent-insensitive).

Lineage: byte-identical to the output of `experiments/2026-03-21-c5-subtlex/`
and to `src/data/*.txt`.

## Experiments

`experiments/{YYYY-MM-DD}-{name}/` — one self-contained folder per research
iteration (inputs, script, outputs, README with status). Nothing outside
`experiments/` lives in this folder except the two canonical lists.

| run | input | status |
|---|---|---|
| `2026-03-21-c5-subtlex` | SUBTLEX-PT | **promoted** (current canonical) |
| `2026-05-24-c5-escolex` | ESCOLEX | archived, not promoted |
| `2026-10-16-autostudy` | 10+ corpora + LLM review, agent-driven | recommended candidate, not promoted |

Large inputs (`.xlsx`, `.pdf`) are git-ignored repo-wide; each README says where
to get them.

## Promoting a list

From an experiment folder whose lists share the canonical format (one lowercase
accented word per line, LF):

```
cp output/words-answer.txt output/words-valid.txt ../../        # canonical
cp output/words-answer.txt src/data/answers.txt                  # what the app ships
cp output/words-valid.txt  src/data/valid.txt
```

Then sanity-check against the app's accent logic:
`npx vitest run corpus/experiments/2026-10-16-autostudy/tests`
