#!/usr/bin/env bash
# Rebuild everything from sources/ (run fetch_sources.sh first).
# Python 3.11+ with pandas+openpyxl (step 01 only) and spylls==0.1.7.
# -P keeps the script dir / cwd off sys.path (downloaded data is untrusted).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
PY="python -P"
$PY scripts/01_local_corpora.py
$PY scripts/hunspell_expand.py sources/hunspell_lo/pt_PT work/hun_ptPT_lo_c5.tsv 5
$PY scripts/hunspell_expand.py sources/hunspell_lo/pt_PT work/hun_ptPT_lo_all.tsv 0
$PY scripts/hunspell_expand.py sources/hunspell_lo/pt_BR work/hun_ptBR_lo_c5.tsv 5
$PY scripts/05_wiktionary.py
$PY scripts/10_features.py
$PY scripts/30_review_merge.py > work/review_report.txt     # merges eval/llm_batches -> eval/llm_review.tsv
$PY scripts/20_select.py --no-review --out output/variants/auto
$PY scripts/20_select.py --fam 3.5 --no-review --out output/variants/auto-strict
$PY scripts/20_select.py --no-fem --out output/variants/no-fem
$PY scripts/20_select.py --out output                        # final: rules + LLM review
$PY scripts/eval_br.py > output/eval_br.txt
$PY scripts/40_evaluate.py > /dev/null                       # -> output/metrics.json
$PY scripts/30_review_merge.py output/variants/auto/words-answer.txt output/words-answer.txt | tail -6
$PY scripts/50_blind_score.py
