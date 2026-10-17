"""Loaders for every lexical source used by the experiment.

Each frequency loader returns (counts: dict[str, int], total_tokens: int) over
*all* word lengths, lower-cased, alphabetic-only (Portuguese letters), so that
pre-AO90 spellings of 5-letter words (which may be 6 letters long) can be looked up.
Sources that are missing on disk return empty results, so the pipeline still
runs with a subset of sources.
"""
import csv
import gzip
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
WORK = ROOT / "work"
ALPHA = re.compile(r"^[a-záéíóúâêôãõàüç]+$")


def _add(d, w, c):
    w = w.strip().lower()
    if ALPHA.match(w):
        d[w] = d.get(w, 0) + c


def read_tsv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ── local spreadsheets (exported by 01_local_corpora.py) ───────────────────

def subtlex():
    rows = read_tsv(WORK / "subtlex.tsv")
    counts = {r["word"]: int(float(r["sub_count"])) for r in rows}
    meta = {r["word"]: r for r in rows}
    return counts, sum(counts.values()), meta


def escolex():
    rows = read_tsv(WORK / "escolex.tsv")
    counts = {r["word"]: int(float(r["esc_count"])) for r in rows}
    return counts, sum(counts.values())


def ppal(meta):
    """P-PAL frequency per million (European Portuguese, CETEMPúblico-based),
    shipped as a column of SUBTLEX-PT. Returned as pseudo-counts per 1e6."""
    counts = {}
    for w, r in meta.items():
        try:
            v = float(r["ppal_fmil"])
        except (TypeError, ValueError):
            continue
        if v == v and v > 0:  # not NaN
            counts[w] = v
    return counts, 1_000_000


# ── word-frequency text files ("word count" or "count\tword" per line) ──────

def freq_file(path, word_first=True, sep=None):
    counts = {}
    p = Path(path)
    if not p.exists():
        return {}, 0
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split(sep) if sep else line.split()
            if len(parts) < 2:
                continue
            w, c = (parts[0], parts[-1]) if word_first else (parts[-1], parts[0])
            try:
                _add(counts, w, int(float(c)))
            except ValueError:
                continue
    return counts, sum(counts.values())


def opensubs(lang):
    return freq_file(SRC / "opensubs" / f"{lang}_full.txt")


# Leipzig corpora split by country. The PT/BR ratio uses the news pair only
# (same register); the PT web corpus only feeds familiarity.
LEIPZIG_PT_NEWS = ["por-pt_newscrawl_2011_300K"]
LEIPZIG_BR_NEWS = ["por-br_newscrawl_2011_300K"]
LEIPZIG_PT_WEB = ["por-pt_web_2015_300K"]


def acdc(variety):
    """Linguateca AC/DC form frequencies, all PT ('totalpt') or all BR ('totalbr')
    corpora (CETEMPúblico, CETENFolha, ...). Latin-1, 'freq<TAB>form'."""
    p = SRC / "linguateca" / f"formas.total{variety}.txt"
    counts = {}
    if not p.exists():
        return {}, 0
    with open(p, encoding="latin-1") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2:
                try:
                    _add(counts, parts[1], int(parts[0]))
                except ValueError:
                    pass
    return counts, sum(counts.values())


def corlex():
    """CLUL CORLEX / LMCPC (16M-word European Portuguese corpus). Form lines look
    like 'form (POS) # freq'; lemma lines start with '@' and are skipped."""
    p = SRC / "corlex" / "lmcpc_dec.txt"
    counts = {}
    if not p.exists():
        return {}, 0
    with open(p, encoding="latin-1") as fh:
        for line in fh:
            if line.startswith("@") or "#" not in line:
                continue
            left, _, freq = line.rpartition("#")
            form = left.split("(")[0].strip()
            try:
                _add(counts, form, int(freq))
            except ValueError:
                pass
    return counts, sum(counts.values())


def natura_wordlist(variant):
    """Natura full-form wordlist ('ao' or 'preao'), Latin-1, one form per line."""
    p = SRC / "natura" / f"wordlist-{variant}.txt.xz"
    if not p.exists():
        return set()
    import lzma
    with lzma.open(p, "rt", encoding="latin-1") as fh:
        return {w.strip() for w in fh if w.strip()}


def languagetool_pairs():
    """LanguageTool dialect_alternations.txt: list of (br_form, pt_form)."""
    p = SRC / "languagetool" / "dialect_alternations.txt"
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            br, pt = line.split("=", 1)
            out.append((br.strip(), pt.strip()))
    return out


def leipzig(name):
    """Leipzig Corpora Collection: '<name>-words.txt' inside <name>.tar.gz
    (columns: id, word, freq). Extracted words files are cached in work/."""
    cache = WORK / f"leipzig_{name}.tsv"
    if not cache.exists():
        tgz = SRC / "leipzig" / f"{name}.tar.gz"
        if not tgz.exists():
            return {}, 0
        counts = {}
        with tarfile.open(tgz) as tf:
            member = next(m for m in tf.getmembers() if m.name.endswith("-words.txt"))
            fh = tf.extractfile(member)
            for raw in fh:
                parts = raw.decode("utf-8", "replace").rstrip("\n").split("\t")
                if len(parts) >= 3:
                    try:
                        _add(counts, parts[1], int(parts[2]))
                    except ValueError:
                        pass
        with open(cache, "w", encoding="utf-8") as out:
            for w, c in counts.items():
                out.write(f"{w}\t{c}\n")
    return freq_file(cache, sep="\t")


# ── dictionaries ────────────────────────────────────────────────────────────

def hunspell_forms(tag):
    """5-letter expansion produced by hunspell_expand.py: {form: row}."""
    p = WORK / f"hun_{tag}_c5.tsv"
    if not p.exists():
        return {}
    return {r["form"]: r for r in read_tsv(p)}


def wiktionary():
    """Per-word summary built by 05_wiktionary.py: {word: row}."""
    p = WORK / "wiktionary_c5.tsv"
    if not p.exists():
        return {}
    return {r["word"]: r for r in read_tsv(p)}


def gold(name):
    p = ROOT / "eval" / f"gold_{name}.txt"
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        w = line.split("#")[0].strip()
        if w:
            out.append(w)
    return out
