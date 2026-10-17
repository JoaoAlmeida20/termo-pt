#!/usr/bin/env python3
"""Expand a Hunspell dictionary (unmunch) and keep the forms of a given length.

Usage: python -P hunspell_expand.py <dict_base_path> <out.tsv> [length]   (length 0 = all)

Output columns: form, lemma, cat (Natura CAT= tag of the lemma, if any),
tense (T= tag, e.g. inf), preao (PREAO90= spelling of the lemma, if any),
derived (0 = the dictionary stem itself, 1 = produced by an affix rule),
morph (morphological field of the affix rule(s), e.g. '+N=p' plural, '+G=f').

Uses spylls only to parse the .aff file; the expansion itself is a plain
stem x suffix x (cross-product) prefix walk, including two-level suffixes.
"""
import re
import sys
from pathlib import Path

from spylls.hunspell import Dictionary

ALPHA = re.compile(r"^[a-záéíóúâêôãõàüç]+$")
LEMMA_LIKE = {"+G=f", "+G=f,N=s", "+G=f,N=s,T=ppa", "+G=m,N=s,T=ppa"}


def apply(affix, stem, is_suffix):
    if not affix.cond_regexp.search(stem):
        return None
    if is_suffix:
        base = stem[: len(stem) - len(affix.strip)] if affix.strip else stem
        return base + affix.add
    base = stem[len(affix.strip):] if affix.strip else stem
    return affix.add + base


def read_morph(aff_path):
    """Map (kind, flag, strip, add, condition) -> morphological field of the rule,
    e.g. '+N=p' (plural) or '+G=f' (feminine). spylls doesn't keep this field."""
    morph = {}
    for line in Path(aff_path).read_text(encoding="utf-8-sig").splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[0] in ("SFX", "PFX"):  # header lines have 4 fields
            kind, flag, strip, add, cond = parts[:5]
            strip = "" if strip == "0" else strip
            add = "" if add.split("/")[0] == "0" else add.split("/")[0]
            morph[(kind, flag, strip, add, cond)] = " ".join(parts[5:])
    return morph


def _m(morph, kind, affix):
    return morph.get((kind, affix.flag, affix.strip, affix.add, affix.condition), "")


def expand_word(stem, flags, aff, forbidden, morph):
    """Yield (form, derived, morph) for one dictionary entry."""
    if forbidden and forbidden in flags:
        return
    yield stem, 0, ""
    suffixed = []
    for fl in flags:
        for sfx in aff.SFX.get(fl, []):
            f = apply(sfx, stem, True)
            if f is None:
                continue
            m1 = _m(morph, "SFX", sfx)
            suffixed.append((f, sfx, m1))
            yield f, 1, m1
            # two-level suffixes (continuation flags on the suffix)
            for fl2 in sfx.flags:
                for sfx2 in aff.SFX.get(fl2, []):
                    f2 = apply(sfx2, f, True)
                    if f2 is not None:
                        yield f2, 1, (m1 + " " + _m(morph, "SFX", sfx2)).strip()
    for fl in flags:
        for pfx in aff.PFX.get(fl, []):
            f = apply(pfx, stem, False)
            if f is None:
                continue
            mp = _m(morph, "PFX", pfx)
            yield f, 1, mp
            if pfx.crossproduct:
                for sf, sfx, m1 in suffixed:
                    if sfx.crossproduct:
                        f2 = apply(pfx, sf, False)
                        if f2 is not None:
                            yield f2, 1, (mp + " " + m1).strip()


def read_cats(dic_path):
    """Natura dictionaries annotate entries as 'stem/FLAGS<TAB>[CAT=..,G=..]'.
    Returns ({stem: (cat, tense, preao)}, verb_stems) where verb_stems are stems
    listed as conjugated forms of another verb ('tinha [$ter$...T=pi]')."""
    cats, verb_stems = {}, set()
    for line in Path(dic_path).read_text(encoding="utf-8-sig").splitlines()[1:]:
        if "[" in line:
            stem = line.split("/")[0].split("\t")[0].strip()
            ann = dict(kv.split("=", 1) for kv in re.findall(r"[A-Z0-9]+=[^,\]]+", line))
            if "[$" in line and ann.get("T") not in ("inf", None):
                verb_stems.add(stem)
                continue
            cats.setdefault(stem, (ann.get("CAT", ""), ann.get("T", ""), ann.get("PREAO90", "")))
    return cats, verb_stems


def preao_form(form, lemma, preao):
    """Best-effort pre-AO90 spelling of an inflected form, given the lemma's
    AO90 and pre-AO90 spellings (e.g. atores / ator / actor -> actores)."""
    if not preao:
        return ""
    k = 0
    while k < min(len(form), len(lemma)) and form[k] == lemma[k]:
        k += 1
    if k < len(lemma) - 2:
        return ""
    return preao[: k + len(preao) - len(lemma)] + form[k:]


def main(base, out, n=5):
    d = Dictionary.from_files(base)
    cats, verb_forms = read_cats(base + ".dic")
    morph = read_morph(base + ".aff")
    forbidden = getattr(d.aff, "FORBIDDENWORD", None)
    seen = {}
    for w in d.dic.words:
        lemma = w.stem
        for form, derived, mo in expand_word(lemma, w.flags, d.aff, forbidden, morph):
            if (n and len(form) != n) or not ALPHA.match(form):
                continue
            if "T=" in mo and "T=ppa" not in mo:
                verb_forms.add(form)   # conjugated form (participles excluded)
            # keep the most lemma-like analysis: stem < feminine/participle < other
            rank = 0 if not derived else 1 if mo in LEMMA_LIKE else 2
            prev = seen.get(form)
            if prev is None or rank < prev[4]:
                seen[form] = (lemma, cats.get(lemma, ("", "", "")), derived, mo, rank)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("form\tlemma\tcat\ttense\tpreao\tderived\tmorph\tverbform\n")
        for form in sorted(seen):
            lemma, (cat, tense, preao), derived, mo, _ = seen[form]
            fh.write(f"{form}\t{lemma}\t{cat}\t{tense}\t{preao_form(form, lemma, preao)}\t{derived}\t{mo}"
                     f"\t{int(form in verb_forms)}\n")
    print(out, len(seen))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 5)
