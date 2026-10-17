#!/usr/bin/env python3
"""Compare word lists: current canonical lists vs the experiment outputs.

Valid-list metrics
  - size
  - EP token coverage: share of 5-letter word *tokens* (Portuguese letters only)
    in an EP corpus that the list accepts, i.e. how rarely a real EP word typed by
    a player would be rejected (proper names excluded: names are never valid).
    Measured on CORLEX (CLUL) and AC/DC-PT, which do
    not drive the valid-list rules (those use Natura/SUBTLEX/OpenSubtitles).
  - BR leakage: entries flagged Brazilian by the deterministic spelling rules
    (accent rule / Wiktionary BR-only) or by the frequency ratio
  - accent collisions: accent-stripped keys with more than one spelling

Answer-list metrics
  - size, share of plurals (ends in -s and not in Natura as a stem), BR-flagged,
    not in pt_PT, accent collisions with the valid list
Writes output/metrics.json for the report.
"""
import collections
import importlib.util
import json
import math
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

spec = importlib.util.spec_from_file_location("sel", Path(__file__).resolve().parent / "20_select.py")
sel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sel)

CORPUS_DIR = S.ROOT.parents[1]


def strip(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")


def load(p):
    return [w.strip() for w in Path(p).read_text(encoding="utf-8").splitlines() if w.strip()]


def coverage(words, counts):
    keys = {strip(w) for w in words}
    tot = cov = 0
    missed = collections.Counter()
    for w, c in counts.items():
        if len(w) == 5:
            tot += c
            if strip(w) in keys:
                cov += c
            else:
                missed[w] = c
    return cov / tot, missed


def main():
    F = {r["word"]: r for r in S.read_tsv(S.WORK / "features_c5.tsv")}
    clx, _ = S.corlex()
    acdc, _ = S.acdc("pt")
    # only count corpus forms some dictionary knows (drops names / typos / foreign)
    # proper names (jorge, braga, japão) are excluded by design, so they don't count
    natura = {w for w in S.natura_wordlist("ao") if len(w) == 5 and w.islower()}
    known = natura | {w for w, r in F.items()
                      if r["in_pt"] == "1" or (r["wk_has_name"] != "1" and r["in_wik"] == "1")}
    clx = {w: c for w, c in clx.items() if w in known}
    acdc = {w: c for w, c in acdc.items() if w in known}

    valid_lists = {
        "current": load(CORPUS_DIR / "words-valid.txt"),
        "escolex-run": load(CORPUS_DIR / "2026-05-24-c5-escolex" / "words-valid.txt"),
        "experiment": load(S.ROOT / "output" / "words-valid.txt"),
    }
    answer_lists = {
        "current": load(CORPUS_DIR / "words-answer.txt"),
        "escolex-run": load(CORPUS_DIR / "2026-05-24-c5-escolex" / "words-answer.txt"),
        "experiment-auto": load(S.ROOT / "output" / "variants" / "auto" / "words-answer.txt"),
        "experiment": load(S.ROOT / "output" / "words-answer.txt"),
    }
    metrics = {"valid": {}, "answers": {}}
    for name, ws in valid_lists.items():
        c1, m1 = coverage(ws, clx)
        c2, m2 = coverage(ws, acdc)
        br_sp = [w for w in ws if w in F and sel.br_spelling(F[w])]
        br_fr = [w for w in ws if w in F and sel.br_freq(F[w]) and not sel.br_spelling(F[w])]
        keys = collections.Counter(strip(w) for w in ws)
        coll = sum(1 for k, n in keys.items() if n > 1)
        not_dict = [w for w in ws if w not in F]
        metrics["valid"][name] = {
            "size": len(ws), "cov_corlex": round(c1, 4), "cov_acdc": round(c2, 4),
            "br_spelling": len(br_sp), "br_freq": len(br_fr), "accent_collisions": coll,
            "not_in_any_dictionary": len(not_dict),
            "examples_br": br_sp[:15], "examples_not_dict": not_dict[:15],
            "top_missed_corlex": [w for w, _ in m1.most_common(15)],
        }
    valid_keys = {strip(w) for w in valid_lists["experiment"]}
    for name, ws in answer_lists.items():
        rows = [F.get(w) for w in ws]
        plural = sum(1 for w, r in zip(ws, rows) if w.endswith("s") and not (r and r["pt_derived"] == "0"))
        br = [w for w, r in zip(ws, rows) if r and sel.is_br(r)]
        notpt = [w for w, r in zip(ws, rows) if not r or r["in_pt"] != "1"]
        fams = [sel.fam(r) for r in rows if r]
        metrics["answers"][name] = {
            "size": len(ws), "plural_like": plural, "br_flagged": len(br), "not_in_pt_PT": len(notpt),
            "median_fam": round(sorted(fams)[len(fams) // 2], 2) if fams else None,
            "examples_br": br[:15], "examples_not_pt": notpt[:15],
            "keys_missing_from_experiment_valid": sum(strip(w) not in valid_keys for w in ws),
        }

    old_v, new_v = set(valid_lists["current"]), set(valid_lists["experiment"])
    new_keys = {strip(w) for w in new_v}
    dropped = sorted(w for w in old_v if strip(w) not in new_keys)
    reasons = collections.Counter()
    ex = collections.defaultdict(list)
    for w in dropped:
        r = F.get(w)
        why = ("not in any dictionary" if r is None else "brazilian" if sel.is_br(r)
               else "no EP evidence / not in pt_PT")
        reasons[why] += 1
        ex[why].append(w)
    metrics["valid_dropped_from_current"] = {
        "count": len(dropped), "by_reason": dict(reasons),
        "examples": {k: v[:25] for k, v in ex.items()},
    }
    metrics["valid_added_vs_current"] = len({strip(w) for w in new_v} - {strip(w) for w in old_v})
    (S.ROOT / "output" / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
