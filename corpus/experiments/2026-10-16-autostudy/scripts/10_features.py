#!/usr/bin/env python3
"""Join every source into one feature table: work/features_c5.tsv.

Candidate universe = 5-letter words known to at least one *dictionary*
(Hunspell pt_PT, Hunspell pt_BR, Wiktionary). Corpus-only strings are mostly
typos, names and foreign words, so they are not candidates.

Frequency features are Zipf values (log10 per-billion, +1 smoothing). For
AO90 forms, the counts of their pre-AO90 spelling are added (SUBTLEX-PT and
most corpora predate the reform: 'actor' feeds 'ator').
"""
import math
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -P
import sources as S  # noqa: E402

OUT = S.WORK / "features_c5.tsv"


def strip_accents(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")


def zipf(c, total):
    return round(math.log10((c + 1) / total * 1e9), 3) if total else ""


def br_ratio(c_br, t_br, c_pt, t_pt):
    """log2 of BR relative frequency over EP relative frequency (+1 smoothing)."""
    if not t_br or not t_pt:
        return ""
    return round(math.log2(((c_br + 1) / t_br) / ((c_pt + 1) / t_pt)), 3)


def main():
    hun_pt = S.hunspell_forms("ptPT_lo")
    hun_br = S.hunspell_forms("ptBR_lo")
    wik = S.wiktionary()
    sub, sub_t, sub_meta = S.subtlex()
    esc, esc_t = S.escolex()
    ppal, ppal_t = S.ppal(sub_meta)
    os_pt, os_pt_t = S.opensubs("pt")
    os_br, os_br_t = S.opensubs("pt_br")
    lz_pt = merge([S.leipzig(n) for n in S.LEIPZIG_PT_NEWS])
    lz_br = merge([S.leipzig(n) for n in S.LEIPZIG_BR_NEWS])
    lz_web, lz_web_t = merge([S.leipzig(n) for n in S.LEIPZIG_PT_WEB])
    acdc_pt, acdc_pt_t = S.acdc("pt")
    acdc_br, acdc_br_t = S.acdc("br")
    clx, clx_t = S.corlex()
    natura_ao = {w for w in S.natura_wordlist("ao") if len(w) == 5 and w.islower()}  # names are capitalised

    cands = set(hun_pt) | set(hun_br) | {w for w, r in wik.items() if r["name_only"] != "1"}
    cands = {w for w in cands if len(w) == 5 and S.ALPHA.match(w)}
    # pre-AO90 spelling of each AO90 form (from Natura's PREAO90 annotation)
    preao = {w: r["preao"] for w, r in hun_pt.items() if r.get("preao") and r["preao"] != w}

    def fcount(counts, w):
        c = counts.get(w, 0)
        p = preao.get(w)
        if p:
            c += counts.get(p, 0)
        return c

    cols = ["word", "key", "in_pt", "in_natura", "in_br", "in_wik", "pt_lemma", "pt_cat", "pt_tense", "pt_derived", "pt_morph", "pt_verbform",
            "preao", "z_sub", "sub_cd", "sub_pos", "z_ppal", "z_esc", "z_ospt", "z_osbr", "z_lzpt",
            "z_lzbr", "z_lzweb", "z_acdcpt", "z_acdcbr", "z_corlex", "br_os", "br_lz", "br_acdc"]
    cols += ["accent_br", "wk_lex_pos", "wk_formof", "wk_lemmas",
                          "wk_br_only", "wk_br_lemma", "wk_pt_variant", "wk_pt_label",
                          "wk_obscure", "wk_obscure_lemma", "wk_vulgar", "wk_superseded", "wk_has_name"]

    pt_spellings = set(hun_pt)
    rows = []
    for w in sorted(cands):
        hp, hb, wk = hun_pt.get(w, {}), hun_br.get(w, {}), wik.get(w, {})
        sm = sub_meta.get(w, {})
        r = {
            "word": w, "key": strip_accents(w),
            "in_pt": int(w in hun_pt), "in_natura": int(w in natura_ao), "in_br": int(w in hun_br), "in_wik": int(w in wik),
            "pt_lemma": hp.get("lemma", ""), "pt_cat": hp.get("cat", ""),
            "pt_tense": hp.get("tense", ""), "pt_derived": hp.get("derived", ""),
            "pt_morph": hp.get("morph", ""), "pt_verbform": hp.get("verbform", ""),
            "preao": preao.get(w, ""),
            "z_sub": zipf(fcount(sub, w), sub_t), "sub_cd": sm.get("sub_cd", ""),
            "sub_pos": sm.get("sub_pos", ""),
            "z_ppal": zipf(fcount(ppal, w) * 1000, ppal_t * 1000),
            "z_esc": zipf(fcount(esc, w), esc_t),
            "z_ospt": zipf(fcount(os_pt, w), os_pt_t), "z_osbr": zipf(os_br.get(w, 0), os_br_t),
            "z_lzpt": zipf(fcount(lz_pt[0], w), lz_pt[1]), "z_lzbr": zipf(lz_br[0].get(w, 0), lz_br[1]),
            "br_os": br_ratio(os_br.get(w, 0), os_br_t, fcount(os_pt, w), os_pt_t),
            "br_lz": br_ratio(lz_br[0].get(w, 0), lz_br[1], fcount(lz_pt[0], w), lz_pt[1]),
            "z_lzweb": zipf(fcount(lz_web, w), lz_web_t),
            "z_acdcpt": zipf(fcount(acdc_pt, w), acdc_pt_t),
            "z_acdcbr": zipf(acdc_br.get(w, 0), acdc_br_t),
            "z_corlex": zipf(fcount(clx, w), clx_t),
            "br_acdc": br_ratio(acdc_br.get(w, 0), acdc_br_t, fcount(acdc_pt, w), acdc_pt_t),
        }
        # deterministic spelling rule: ê/ô where EP writes é/ó (tênis/ténis, gênio/génio).
        # Fires if the é/ó variant is a known EP spelling, or — the general AO90
        # pattern — the circumflex sits before m/n and the word isn't EP-valid.
        ep_var = w.replace("ê", "é").replace("ô", "ó")
        known_ep = ep_var in pt_spellings or ep_var in natura_ao or ep_var in wik
        r["accent_br"] = int(ep_var != w and w not in pt_spellings and w not in natura_ao
                             and (known_ep or bool(re.search("[êô][mn]", w))))
        r.update({
            "wk_lex_pos": wk.get("lex_pos", ""), "wk_formof": wk.get("formof", ""),
            "wk_lemmas": wk.get("lemmas", ""), "wk_br_only": wk.get("br_only", ""),
            "wk_br_lemma": wk.get("br_lemma", ""), "wk_pt_variant": wk.get("pt_variant", ""),
            "wk_pt_label": wk.get("pt_label", ""), "wk_obscure": wk.get("obscure", ""),
            "wk_obscure_lemma": wk.get("obscure_lemma", ""), "wk_vulgar": wk.get("vulgar", ""),
            "wk_superseded": wk.get("superseded", ""), "wk_has_name": wk.get("has_name", ""),
        })
        rows.append(r)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    print(OUT, len(rows), "candidates")
    print("sources: subtlex", sub_t, "| opensubs pt", os_pt_t, "br", os_br_t,
          "| leipzig news pt", lz_pt[1], "br", lz_br[1], "web pt", lz_web_t,
          "| ac/dc pt", acdc_pt_t, "br", acdc_br_t, "| corlex", clx_t)


def merge(pairs):
    counts, total = {}, 0
    for c, t in pairs:
        total += t
        for w, n in c.items():
            counts[w] = counts.get(w, 0) + n
    return counts, total


if __name__ == "__main__":
    main()
