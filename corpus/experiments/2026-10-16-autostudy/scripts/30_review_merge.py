#!/usr/bin/env python3
"""Merge the LLM review batches (eval/llm_batches/out_*.tsv) into
eval/llm_review.tsv and report reviewer agreement and per-list quality.

Duplicated words (seeded across batches) measure self-consistency. When two
reviews disagree, the stricter verdict wins (anything over 'keep') and the
lower familiarity is kept.
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

BATCHES = S.ROOT / "eval" / "llm_batches"
VERDICTS = ["keep", "obscure", "br", "foreign", "vulgar", "inflected", "proper", "error"]


def load_list(path):
    return [w.strip() for w in Path(path).read_text(encoding="utf-8").splitlines() if w.strip()]


def main():
    reviews = collections.defaultdict(list)
    for f in sorted(BATCHES.glob("out_*.tsv")):
        for r in S.read_tsv(f):
            v = (r.get("verdict") or "").strip().lower()
            try:
                fam = int(r.get("fam") or 0)
            except ValueError:
                fam = 0
            reviews[r["word"].strip()].append((v, fam, (r.get("note") or "").strip()))

    # agreement on duplicated words
    dup = {w: rs for w, rs in reviews.items() if len(rs) > 1}
    same_v = sum(rs[0][0] == rs[1][0] for rs in dup.values())
    fam_close = sum(abs(rs[0][1] - rs[1][1]) <= 1 for rs in dup.values())
    disagreements = [(w, rs[0][0], rs[1][0]) for w, rs in dup.items() if rs[0][0] != rs[1][0]]
    bad = [w for w, rs in reviews.items() if any(v not in VERDICTS for v, _, _ in rs)]

    merged = {}
    for w, rs in reviews.items():
        vs = [v for v, _, _ in rs]
        verdict = next((v for v in vs if v != "keep"), "keep")
        merged[w] = (verdict, min(f for _, f, _ in rs), "; ".join(n for _, _, n in rs if n))
    with open(S.ROOT / "eval" / "llm_review.tsv", "w", encoding="utf-8") as fh:
        fh.write("word\tverdict\tfam\tnote\n")
        for w in sorted(merged):
            v, f, n = merged[w]
            fh.write(f"{w}\t{v}\t{f}\t{n}\n")

    print(f"reviewed words: {len(merged)}  invalid verdicts: {bad[:10]}")
    print(f"self-consistency on {len(dup)} duplicates: verdict agreement {same_v}/{len(dup)} "
          f"({same_v / len(dup):.0%}), familiarity within ±1: {fam_close}/{len(dup)} "
          f"({fam_close / len(dup):.0%})")
    print("  disagreements:", disagreements[:30])

    # LLM recall on gold sets
    for g in ("br", "ep", "neutral"):
        ws = [w for w in S.gold(g) if w in merged]
        c = collections.Counter(merged[w][0] for w in ws)
        print(f"gold {g:8}: {dict(c)}")

    return merged


def list_report(merged, lists):
    print(f"\n{'list':28} {'n':>5} {'reviewed':>8} " + " ".join(f"{v[:7]:>7}" for v in VERDICTS) + "  meanfam  fam>=3")
    for name, words in lists.items():
        rev = [w for w in words if w in merged]
        c = collections.Counter(merged[w][0] for w in rev)
        mf = sum(merged[w][1] for w in rev) / max(1, len(rev))
        f3 = sum(merged[w][1] >= 3 for w in rev) / max(1, len(rev))
        print(f"{name:28} {len(words):>5} {len(rev):>8} "
              + " ".join(f"{c[v] / max(1, len(rev)):>7.1%}" for v in VERDICTS)
              + f"  {mf:>6.2f}  {f3:>6.1%}")


if __name__ == "__main__":
    merged = main()
    lists = {
        "current (SUBTLEX) answers": load_list(S.ROOT.parents[1] / "words-answer.txt"),
        "ESCOLEX run answers": load_list(S.ROOT.parents[1] / "2026-05-24-c5-escolex" / "words-answer.txt"),
    }
    for extra in sys.argv[1:]:
        lists[Path(extra).parent.name + "/" + Path(extra).name] = load_list(extra)
    list_report(merged, lists)
