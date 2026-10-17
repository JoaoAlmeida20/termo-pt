#!/usr/bin/env python3
"""Score the blind A/B judgement (eval/blind/judge_*.tsv) per source list.
Judges saw a shuffled, unlabelled mix of words sampled from each list."""
import collections
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

B = S.ROOT / "eval" / "blind"


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def main():
    key = json.loads((B / "blind_key.json").read_text(encoding="utf-8"))
    judges = {f.stem: {r["word"].strip(): r for r in S.read_tsv(f)} for f in sorted(B.glob("judge_*.tsv"))}
    out = {}
    agree = sum(judges["judge_A"][w]["good"] == judges["judge_B"][w]["good"] for w in key)
    print(f"inter-judge agreement (Opus vs Sonnet): {agree}/{len(key)} = {agree / len(key):.0%}")
    for src in ("experiment", "current", "escolex"):
        ws = [w for w, s in key.items() if src in s]
        row = {"n": len(ws)}
        for j, jr in list(judges.items()) + [("both", None)]:
            if jr is None:
                k = sum(all(judges[x][w]["good"] == "1" for x in judges) for w in ws)
            else:
                k = sum(jr[w]["good"] == "1" for w in ws)
            lo, hi = wilson(k, len(ws))
            row[j] = {"good": k, "rate": round(k / len(ws), 3), "ci95": [round(lo, 3), round(hi, 3)]}
        reasons = collections.Counter(judges["judge_A"][w]["reason"] for w in ws if judges["judge_A"][w]["good"] == "0")
        reasons.update(judges["judge_B"][w]["reason"] for w in ws if judges["judge_B"][w]["good"] == "0")
        row["rejection_reasons_both_judges"] = dict(reasons.most_common())
        row["rejected_by_both"] = [w for w in ws if all(judges[x][w]["good"] == "0" for x in judges)]
        out[src] = row
        print(f"{src:11} n={len(ws):3}  A={row['judge_A']['rate']:.1%} {row['judge_A']['ci95']}  "
              f"B={row['judge_B']['rate']:.1%} {row['judge_B']['ci95']}  both={row['both']['rate']:.1%}  "
              f"reasons={dict(reasons.most_common(6))}")
        if src == "experiment":
            print("   rejected by both:", row["rejected_by_both"])
    out["agreement"] = agree / len(key)
    (S.ROOT / "output" / "blind_ab.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
