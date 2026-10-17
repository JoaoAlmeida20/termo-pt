#!/usr/bin/env python3
"""Score each Brazilianism detector on the gold sets (eval/gold_*.txt)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

F = {r["word"]: r for r in S.read_tsv(S.WORK / "features_c5.tsv")}


def num(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


DETECTORS = {
    "opensubs ratio > 1.5": lambda r: num(r["br_os"]) > 1.5,
    "leipzig ratio > 1.5": lambda r: num(r["br_lz"]) > 1.5,
    "AC/DC news ratio > 1.5": lambda r: num(r["br_acdc"]) > 1.5,
    "accent rule (ê/ô vs é/ó)": lambda r: r["accent_br"] == "1",
    "wiktionary BR-only (word or lemma)": lambda r: r["wk_br_only"] == "1" or r["wk_br_lemma"] == "1",
    "not in hunspell pt_PT": lambda r: r["in_pt"] == "0",
}


def combined(r):
    return (DETECTORS["accent rule (ê/ô vs é/ó)"](r)
            or DETECTORS["wiktionary BR-only (word or lemma)"](r)
            or max(num(r["br_os"]), num(r["br_lz"]), num(r["br_acdc"])) > 1.5
            and (num(r["br_os"]) + num(r["br_lz"]) + num(r["br_acdc"])) > 1.5)


DETECTORS["COMBINED"] = combined


def main():
    sets = {k: S.gold(k) for k in ("br", "ep", "neutral")}
    print(f"{'detector':38} {'BR recall':>10} {'EP false+':>10} {'neutral false+':>15}")
    for name, fn in DETECTORS.items():
        res = {}
        for k, ws in sets.items():
            hit = [w for w in ws if w in F and fn(F[w])]
            res[k] = (len(hit), len(ws), hit)
        b, e, n = res["br"], res["ep"], res["neutral"]
        print(f"{name:38} {b[0]:>4}/{b[1]:<5} {e[0]:>4}/{e[1]:<5} {n[0]:>7}/{n[1]:<5}  EP-FP={e[2]} N-FP={n[2]}")
        if name == "COMBINED":
            print("  missed BR:", [w for w in sets["br"] if w not in res["br"][2]])
    print("  gold words absent from candidates:", [w for k in sets for w in sets[k] if w not in F])


if __name__ == "__main__":
    main()


def languagetool_eval():
    """Held-out evaluation on LanguageTool's dialect_alternations (BR=PT pairs,
    never used to build the detectors). Only lower-case 5-letter forms that are
    candidates, and only pairs where both sides differ."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sel", Path(__file__).resolve().parent / "20_select.py")
    sel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sel)
    pairs = [(b, p) for b, p in S.languagetool_pairs() if b != p]
    br_forms = {b for b, p in pairs if len(b) == 5 and b.islower() and b in F}
    pt_forms = {p for b, p in pairs if len(p) == 5 and p.islower() and p in F} - br_forms
    print(f"\nLanguageTool held-out: {len(br_forms)} BR forms, {len(pt_forms)} PT forms in candidates")
    rules = {
        "strong (is_br)": sel.is_br,
        "strong or lean": lambda r: sel.is_br(r) or sel.is_br_lean(r),
        "opensubs>1.5": DETECTORS["opensubs ratio > 1.5"],
        "acdc>1.5": DETECTORS["AC/DC news ratio > 1.5"],
        "accent rule": DETECTORS["accent rule (ê/ô vs é/ó)"],
        "wiktionary": DETECTORS["wiktionary BR-only (word or lemma)"],
        "not in pt_PT": DETECTORS["not in hunspell pt_PT"],
    }
    for name, fn in rules.items():
        tp = sorted(w for w in br_forms if fn(F[w]))
        fp = sorted(w for w in pt_forms if fn(F[w]))
        print(f"  {name:16} BR recall {len(tp)}/{len(br_forms)} ({len(tp)/len(br_forms):.0%})  "
              f"PT false+ {len(fp)}/{len(pt_forms)} ({len(fp)/len(pt_forms):.0%}) {fp[:8]}")
    missed = sorted(w for w in br_forms if not sel.is_br(F[w]))
    print("  missed by strong:", " ".join(missed[:60]))


if __name__ == "__main__":
    languagetool_eval()
