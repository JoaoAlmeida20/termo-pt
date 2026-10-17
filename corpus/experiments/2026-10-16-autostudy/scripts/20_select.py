#!/usr/bin/env python3
"""Build answer / valid lists from work/features_c5.tsv.

Usage: python -P 20_select.py [--fam 3.0] [--out DIR] [--review FILE | --no-review]

ANSWERS — every rule must pass:
  spelling    EP AO90 spelling: in Hunspell pt_PT (Natura), or (in pt_BR/Wiktionary,
              not BR-flagged, and frequent in EP corpora — covers loans like 'lótus')
  shape       a lemma: dictionary stem (any POS except proper noun), or a
              feminine singular / participle form; never a plural or a
              conjugated verb (infinitives OK)
  br          strong Brazilian marker (accent rule, Wiktionary BR-only, or
              PT/BR frequency ratio above the leakage threshold)
  weird       all senses archaic/obsolete/rare/regional (Wiktionary), superseded
              spelling, or mostly vulgar
  rare        EP familiarity score < --fam (mean Zipf over EP corpora)
  review      rejected by the LLM review file (eval/llm_review.tsv)

VALID — permissive but curated: any form in pt_PT (LibreOffice or full Natura
wordlist), plus Wiktionary words (not names, not BR-flagged) with real EP corpus
usage, plus pre-AO90 spellings. Exactly one
spelling per accent-stripped key (answers win, then the most familiar EP form),
because the game maps unaccented input -> one accented form.
"""
import argparse
import math
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

EP_FREQ_COLS = ["z_sub", "z_ospt", "z_lzpt", "z_ppal"]
LEMMA_LIKE = {"+G=f", "+G=f,N=s", "+G=f,N=s,T=ppa", "+G=m,N=s,T=ppa"}  # Natura morphs
BR_STRONG = 3.3   # log2 BR/EP ratio: above this, EP-corpus use is mostly BR leakage
BR_LEAN = 1.5     # between LEAN and STRONG: real EP word that BR uses much more
PROMOTE_FLOOR = 2.25   # with an LLM "keep" (fam>=3), corpus familiarity may be this low
FLOOR_SUB = math.log10(1 / 76_399_640 * 1e9)    # Zipf of a zero count in SUBTLEX-PT
FLOOR_OS = math.log10(1 / 211_702_933 * 1e9)    # ... in OpenSubtitles pt


def num(x, d=None):
    try:
        v = float(x)
        return v if not math.isnan(v) else d
    except (TypeError, ValueError):
        return d


def strip_accents(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")


def fam(r):
    """EP familiarity: mean Zipf over the EP frequency sources that have data.
    P-PAL (newspaper) is only known for words present in SUBTLEX-PT."""
    vals = []
    for c in EP_FREQ_COLS:
        v = num(r.get(c))
        if v is None or (c == "z_ppal" and not r.get("sub_pos")):
            continue
        vals.append(v)
    return sum(vals) / len(vals) if vals else 0.0


def br_ratio(r):
    """Median of the available log2 BR/EP ratios (subtitles, Leipzig news, AC/DC
    news). The median resists one register-specific outlier (e.g. 'cesta' from
    'cesta básica' in Folha de S. Paulo)."""
    ratios = sorted(num(r[c]) for c in ("br_os", "br_lz", "br_acdc") if num(r[c]) is not None)
    if not ratios:
        return None
    m = len(ratios) // 2
    return ratios[m] if len(ratios) % 2 else (ratios[m - 1] + ratios[m]) / 2


def br_spelling(r):
    """Deterministic Brazilian markers (hard rule)."""
    return r["accent_br"] == "1" or r["wk_br_only"] == "1" or r["wk_br_lemma"] == "1"


def br_freq(r):
    """Frequency-ratio Brazilian marker (soft rule). Leakage model: EP subtitles
    ~= EP + ~6.5% BR text (estimated from ônibus/celular/trem), so a ratio above
    ~3.3 means most EP-corpus occurrences are explained by leakage alone."""
    b = br_ratio(r)
    return b is not None and b > BR_STRONG


def is_br(r):
    return br_spelling(r) or br_freq(r)


def is_br_lean(r):
    b = br_ratio(r)
    return b is not None and BR_LEAN < b <= BR_STRONG


def is_weird(r):
    if r["wk_superseded"] == "1":
        return True
    if num(r["wk_obscure"], 0) >= 1 or r["wk_obscure_lemma"] == "1":
        return True
    return num(r["wk_vulgar"], 0) >= 0.5


def spelling_ok(r, f):
    if r["in_pt"] == "1":
        return True
    return (r["in_br"] == "1" or r["in_wik"] == "1") and f >= 3.0 and not is_br(r)


def lemma_shape(r):
    """Return (label, soft) for the word's shape, or (None, False) if it can't be
    an answer. soft=True marks verb homographs (chama, cobra, tinha) that the
    automatic mode rejects but a reviewer may accept."""
    wk_lex = set(filter(None, r["wk_lex_pos"].split(",")))
    wk_form = set(filter(None, r["wk_formof"].split(",")))
    lemma_like = r["in_pt"] == "1" and r["pt_derived"] == "1" and r["pt_morph"] in LEMMA_LIKE
    # Wiktionary knows it only as a plural and/or verb form (artes, lares, apaga);
    # Natura's participle analysis (doado, suada) takes precedence
    if not wk_lex and wk_form and wk_form <= {"plural", "verb", "other"} and not lemma_like:
        return None, False
    # feminine singular form of an adjective/noun (leiga, gasta, turva)
    if "fem" in wk_form and not r["word"].endswith("s") and not lemma_like and r["in_pt"] == "1":
        return "wik-fem", False
    if r["in_pt"] == "1":
        cat, morph = r["pt_cat"], r["pt_morph"]
        if cat == "np":
            # AO90 lower-cases months/seasons (abril, verão): Natura still tags
            # them np; accept softly when Wiktionary has a lower-case lexical entry
            return ("np-lower", True) if wk_lex - {"name"} else (None, False)
        if cat == "cp":   # contractions (desta, daqui, disso): reviewer decides
            return "contraction", True
        infinitive = cat == "v" and r["pt_tense"] == "inf" and r["pt_derived"] == "0"
        # homograph of a conjugated verb whose dominant reading is verbal
        # (tinha 'ringworm' vs tinha < ter): SUBTLEX lists PoS by frequency
        soft = (not infinitive and r["pt_verbform"] == "1"
                and r["sub_pos"].split(",")[0] == "V")
        if r["pt_derived"] == "0":
            if cat == "v" and r["pt_tense"] not in ("inf", ""):
                return None, False
            return "stem:" + cat, soft
        if morph in LEMMA_LIKE:
            return "derived:" + morph, soft   # feminine / participle-as-adjective
        return None, False
    # not in Natura: trust Wiktionary lexical POS, reject pure form-of words
    if not wk_lex or wk_lex <= {"name", "suffix", "prefix", "contraction"}:
        return None, False
    if r["word"].endswith("s") and "plural" in wk_form:
        return None, False
    # also a proper name (Japão, Júlio): the lower-case entry is usually marginal
    return "wik:" + "/".join(sorted(wk_lex)), r.get("wk_has_name") == "1"


def is_feminine_form(r):
    """Feminine singular derived from a masculine lemma (obesa < obeso)."""
    label = lemma_shape(r)[0] or ""
    return label in ("derived:+G=f", "derived:+G=f,N=s", "derived:+G=f,N=s,T=ppa", "wik-fem")


def ep_evidence(r):
    """Real EP usage: >= 3 occurrences in SUBTLEX-PT or >= 20 in OpenSubtitles-pt
    (z values carry +1 smoothing, so a zero count sits exactly at the floor)."""
    return (num(r["z_sub"], 0) >= math.log10(4 / 76_399_640 * 1e9)
            or num(r["z_ospt"], 0) >= math.log10(21 / 211_702_933 * 1e9))


def valid_ok(r):
    """Valid-guess admission. Hunspell/Natura pt_PT forms always; otherwise a
    Wiktionary entry that is not a proper name, not Brazilian, with real EP
    usage. pt_BR (VERO) alone is not enough: it lower-cases names (laura,
    jones) and OpenSubtitles carries stray foreign tokens (gotta, mamma)."""
    if r["in_pt"] == "1" or r["in_natura"] == "1":
        return True
    if r["in_wik"] != "1" or r.get("wk_has_name") == "1" or is_br(r):
        return False
    if num(r["wk_obscure"], 0) >= 1 or r["wk_superseded"] == "1" and r["preao"] == "":
        return False   # archaic-only entries (nella, annos, muyto)
    wk_lex = set(filter(None, r["wk_lex_pos"].split(","))) - {"name"}
    return bool(wk_lex or r["wk_formof"]) and ep_evidence(r)


def load_review(path):
    if not path or not Path(path).exists():
        return {}
    return {r["word"]: r for r in S.read_tsv(path)}


def classify(rows, fam_min, review):
    """Return (answers, reasons, valid) where reasons[word] lists failed rules.

    Hard rules always apply. Soft rules (verb homograph, Wiktionary obscurity,
    BR frequency ratio, corpus rarity down to PROMOTE_FLOOR) apply only when the
    word has no reviewer 'keep' with familiarity >= 3."""
    answers, reasons, valid = [], {}, {}
    for r in rows:
        w = r["word"]
        f = r["_fam"] = fam(r)
        hard, soft = [], []
        if not spelling_ok(r, f):
            # outside Natura but in pt_BR/Wiktionary and not Brazilian (lótus,
            # islão, sifão): only the 'frequent enough' part is soft
            in_dict = r["in_br"] == "1" or r["in_wik"] == "1"
            (soft if in_dict and not is_br(r) else hard).append("spelling")
        label, homograph = lemma_shape(r)
        if label is None:
            hard.append("shape")
        elif homograph:
            soft.append("homograph")
        if br_spelling(r):
            hard.append("br")
        elif br_freq(r):
            soft.append("br-freq")
        if is_weird(r):
            soft.append("weird")
        if f < PROMOTE_FLOOR:
            hard.append("rare")
        elif f < fam_min:
            soft.append("rare")
        rv = review.get(w)
        endorsed = bool(rv) and rv.get("verdict") == "keep" and int(rv.get("fam") or 0) >= 3
        if rv and not endorsed:
            hard.append("review:" + (rv["verdict"] if rv.get("verdict") != "keep" else "unfamiliar"))
        why = hard + ([] if endorsed else soft)
        reasons[w] = why
        if not why:
            answers.append(r)
        if valid_ok(r):
            valid[w] = r
    return answers, reasons, valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fam", type=float, default=3.0)
    ap.add_argument("--out", default=str(S.ROOT / "output"))
    ap.add_argument("--review", default=str(S.ROOT / "eval" / "llm_review.tsv"))
    ap.add_argument("--no-review", action="store_true")
    ap.add_argument("--no-preao", action="store_true", help="don't add pre-AO90 spellings to valid")
    ap.add_argument("--no-fem", action="store_true",
                    help="exclude feminine forms of adjectives/nouns (obesa, tonta) from answers")
    args = ap.parse_args()

    rows = S.read_tsv(S.WORK / "features_c5.tsv")
    review = {} if args.no_review else load_review(args.review)
    answers, reasons, valid = classify(rows, args.fam, review)
    if args.no_fem:
        answers = [r for r in answers if not is_feminine_form(r)]

    # One spelling per accent-stripped key; answers win, then familiarity.
    # Answers are never dropped: scoring is accent-insensitive, so an answer only
    # needs its key to be valid ('louça' still works when 'louca' is displayed).
    answer_set = {r["word"] for r in answers}
    by_key = {}
    for w, r in valid.items():
        score = (w in answer_set, not br_spelling(r), r["in_pt"] == "1", r["_fam"])
        best = by_key.get(r["key"])
        if best is None or score > best[0]:
            by_key[r["key"]] = (score, w)
    for r in answers:   # make sure every answer's key is guessable
        by_key.setdefault(r["key"], ((True, True, True, r["_fam"]), r["word"]))
    shadowed = sorted(w for w in valid if by_key[valid[w]["key"]][1] != w)

    # pre-AO90 spellings (acção, actor, tecto, jóias...) as extra valid guesses,
    # only when their accent-stripped key is still free
    preao_added = []
    if not args.no_preao:
        for h in S.read_tsv(S.WORK / "hun_ptPT_lo_all.tsv"):
            p = h["preao"]
            if len(p) == 5 and p == p.lower() and p != h["form"]:
                k = strip_accents(p)
                if k not in by_key:
                    by_key[k] = ((False, False, False, 0), p)
                    preao_added.append(p)
    valid_words = sorted(w for _, w in by_key.values())

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "words-answer.txt").write_text("\n".join(sorted(answer_set)) + "\n", encoding="utf-8")
    (out / "words-valid.txt").write_text("\n".join(valid_words) + "\n", encoding="utf-8")
    with open(out / "answers-scored.tsv", "w", encoding="utf-8") as fh:
        fh.write("word\tfam\tshape\tbr_lean\n")
        for r in sorted(answers, key=lambda r: -r["_fam"]):
            fh.write(f"{r['word']}\t{r['_fam']:.3f}\t{lemma_shape(r)[0]}\t{int(is_br_lean(r))}\n")
    with open(S.WORK / "reasons.tsv", "w", encoding="utf-8") as fh:
        fh.write("word\tfam\treasons\tbr_lean\tshape\n")
        for r in rows:
            fh.write(f"{r['word']}\t{r['_fam']:.3f}\t{','.join(reasons[r['word']])}\t"
                     f"{int(is_br_lean(r))}\t{lemma_shape(r)[0] or ''}\n")
    print(f"answers={len(answers)} valid={len(valid_words)} (pre-AO added {len(preao_added)}: "
          f"{' '.join(preao_added)}; accent-shadowed spellings {len(shadowed)})")


if __name__ == "__main__":
    main()
