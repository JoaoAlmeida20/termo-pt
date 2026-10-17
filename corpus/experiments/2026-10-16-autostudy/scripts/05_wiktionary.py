#!/usr/bin/env python3
"""Summarise the kaikki.org English-Wiktionary Portuguese dump per 5-letter word.

Input : sources/wiktionary/kaikki-pt.jsonl.gz
Output: work/wiktionary_c5.tsv with one row per 5-letter (lower-case) headword:

  lex_pos       POS of entries that have real (non form-of) senses
  formof        form-of kinds: plural / fem / verb / alt  (comma-separated)
  lemmas        lemmas this word is a form of
  n_lex         number of lexical senses (across lexical entries)
  n_br, n_pt    lexical senses tagged Brazil(-region) / Portugal(-region)
  br_label      1 if a head label says "Brazilian Portuguese spelling/form" or
                the word is in category "Brazilian Portuguese" only
  pt_label      1 if labelled "European Portuguese spelling/form" or category
  n_form, n_form_br  form-of/alt-of senses, and those tagged Brazil (e.g. bebê)
  pt_variant    1 if the entry lists an alternative form tagged Portugal (tchau -> xau)
  br_only       1 if every sense (lexical or form-of) is Brazil-tagged (senses of an
                entry whose head is labelled Brazilian count as Brazil-tagged)
  obscure       fraction of lexical senses tagged archaic/obsolete/rare/...
  vulgar        fraction of lexical senses tagged vulgar/offensive/derogatory/slur
  superseded    1 if spelling is categorised as superseded (1911..AO1990)
  name_only     1 if every entry is a proper name
  has_name      1 if some entry is a proper name (Japão, Júlio)
  br_lemma      for form-of words: 1 if all their lemmas are Brazil-only
  obscure_lemma for form-of words: 1 if all their lemmas are obscure-only
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5

BR_TAGS = {"Brazil", "South-Brazil", "Northeast-Brazil", "São-Paulo", "Rio-de-Janeiro",
           "Rio-Grande-do-Sul", "Minas-Gerais", "Bahia", "Pernambuco", "Amazonas", "Pará",
           "Northern-Brazil", "Southeast-Brazil", "Central-Brazil"}
PT_TAGS = {"Portugal", "Azores", "Madeira", "Northern-Portugal", "Southern-Portugal",
           "Alentejo", "Algarve", "Minho", "Trás-os-Montes", "Lisbon", "Porto"}
OBSCURE_TAGS = {"archaic", "obsolete", "dated", "rare", "nonstandard", "misspelling",
                "pronunciation-spelling", "dialectal", "regional", "uncommon", "poetic",
                "Angola", "Mozambique", "Cape-Verde", "Guinea-Bissau", "Timor", "Goa",
                "eye-dialect", "historical"}
VULGAR_TAGS = {"vulgar", "offensive", "derogatory", "slur", "ethnic"}


def is_form(sense):
    t = set(sense.get("tags", []))
    return bool({"form-of", "alt-of"} & t) or "form_of" in sense or "alt_of" in sense


def formof_kind(sense, pos):
    t = set(sense.get("tags", []))
    if "alt-of" in t or "alt_of" in sense:
        return "alt"
    if pos == "verb":
        return "verb"
    if "plural" in t:
        return "plural"
    if "feminine" in t:
        return "fem"
    return "other"


def main():
    src = ROOT / "sources" / "wiktionary" / "kaikki-pt.jsonl.gz"
    words = defaultdict(lambda: {
        "lex_pos": set(), "formof": set(), "lemmas": set(), "n_lex": 0, "n_br": 0, "n_pt": 0,
        "br_label": 0, "pt_label": 0, "n_obscure": 0, "n_vulgar": 0, "superseded": 0,
        "n_form": 0, "n_form_br": 0, "pt_variant": 0, "entries": 0, "names": 0})
    with gzip.open(src, "rt", encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            if d.get("lang_code", "pt") != "pt":
                continue
            raw = d.get("word", "")
            w = raw.lower()
            pos = d.get("pos", "")
            rec = words[w]
            rec["entries"] += 1
            if pos == "name" or (raw[:1].isupper() and w != raw):
                rec["names"] += 1
                continue
            entry_br = entry_pt = False   # head labels apply to this entry's senses only
            for h in d.get("head_templates", []):
                if h.get("name") in ("tlb", "lb", "tlb-lite"):
                    label = " ".join(v for k, v in h.get("args", {}).items() if k != "1")
                    if "Brazilian Portuguese" in label or label.startswith("Brazil"):
                        rec["br_label"] = 1
                        entry_br = True
                    if "European Portuguese" in label or label.startswith("Portugal"):
                        rec["pt_label"] = 1
                        entry_pt = True
            for fo in d.get("forms", []):
                ft = set(fo.get("tags", []))
                if "alternative" in ft and ft & PT_TAGS and not ft & BR_TAGS:
                    rec["pt_variant"] = 1
            for s in d.get("senses", []):
                tags = set(s.get("tags", []))
                cats = {c.get("name", "") for c in s.get("categories", [])}
                if entry_br and not entry_pt:
                    tags.add("Brazil")
                if entry_pt and not entry_br:
                    tags.add("Portugal")
                if any("superseded" in c for c in cats):
                    rec["superseded"] = 1
                if is_form(s):
                    rec["formof"].add(formof_kind(s, pos))
                    rec["n_form"] += 1
                    cat_br = "Brazilian Portuguese" in cats and "European Portuguese" not in cats
                    rec["n_form_br"] += (bool(tags & BR_TAGS) or cat_br) and not tags & PT_TAGS
                    for fo in s.get("form_of", []) + s.get("alt_of", []):
                        if fo.get("word"):
                            rec["lemmas"].add(fo["word"].lower())
                    continue
                rec["lex_pos"].add(pos)
                rec["n_lex"] += 1
                br, pt = bool(tags & BR_TAGS), bool(tags & PT_TAGS)
                rec["n_br"] += br and not pt
                rec["n_pt"] += pt and not br
                rec["n_obscure"] += bool(tags & OBSCURE_TAGS)
                rec["n_vulgar"] += bool(tags & VULGAR_TAGS)

    def br_only(r):
        total = r["n_lex"] + r["n_form"]
        return total > 0 and r["n_br"] + r["n_form_br"] == total

    def obscure_only(r):
        return r["n_lex"] > 0 and r["n_obscure"] == r["n_lex"]

    out = ROOT / "work" / f"wiktionary_c{N}.tsv"
    cols = ["word", "lex_pos", "formof", "lemmas", "n_lex", "n_br", "n_pt", "br_label",
            "pt_label", "n_form", "n_form_br", "pt_variant", "br_only", "obscure", "vulgar",
            "superseded", "name_only", "has_name", "br_lemma", "obscure_lemma"]
    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for w, r in sorted(words.items()):
            if len(w) != N or not w.isalpha():
                continue
            # only pure form-of words (no lexical sense of their own) inherit lemma flags
            lem = [words[l] for l in r["lemmas"] if l in words] if not r["n_lex"] else []
            row = {
                "word": w,
                "lex_pos": ",".join(sorted(r["lex_pos"])),
                "formof": ",".join(sorted(r["formof"])),
                "lemmas": ",".join(sorted(r["lemmas"])),
                "n_lex": r["n_lex"], "n_br": r["n_br"], "n_pt": r["n_pt"],
                "br_label": r["br_label"], "pt_label": r["pt_label"],
                "n_form": r["n_form"], "n_form_br": r["n_form_br"], "pt_variant": r["pt_variant"],
                "br_only": int(br_only(r)),
                "obscure": round(r["n_obscure"] / r["n_lex"], 2) if r["n_lex"] else "",
                "vulgar": round(r["n_vulgar"] / r["n_lex"], 2) if r["n_lex"] else "",
                "superseded": r["superseded"],
                "name_only": int(r["entries"] > 0 and r["names"] == r["entries"]),
                "has_name": int(r["names"] > 0),
                "br_lemma": int(bool(lem) and all(br_only(x) for x in lem)),
                "obscure_lemma": int(bool(lem) and all(obscure_only(x) for x in lem)),
            }
            fh.write("\t".join(str(row[c]) for c in cols) + "\n")
            n += 1
    print(out, n)


if __name__ == "__main__":
    main()
