#!/usr/bin/env python3
"""Export SUBTLEX-PT and ESCOLEX (all word lengths) from the local spreadsheets
into work/*.tsv so later steps don't need pandas/openpyxl. All lengths are kept
because pre-AO90 spellings (e.g. 'actor') feed the frequency of AO90 5-letter
forms ('ator')."""
import warnings
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)
HERE = Path(__file__).resolve().parent
INPUTS = HERE.parent / "inputs"   # subtlex_pt.xlsx + ESCOLEX.xlsx live with the experiment
WORK = HERE.parent / "work"
ALPHA = r"^[a-záéíóúâêôãõàüç]+$"


def export(path, sheet, cols, out):
    df = pd.read_excel(INPUTS / path, sheet_name=sheet, usecols=list(cols))
    df = df.rename(columns=cols)
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"].str.match(ALPHA)]
    df = df.groupby("word", as_index=False).first()
    df.to_csv(WORK / out, sep="\t", index=False)
    print(out, len(df))


if __name__ == "__main__":
    export("subtlex_pt.xlsx", "SUBTLEX-PT",
           {"Wordform": "word", "SUBTLEX_FREQcount": "sub_count", "SUBTLEXZipf": "sub_zipf",
            "SUBTLEX_CDcount": "sub_cd", "P-PALfreq": "ppal_fmil", "PoS": "sub_pos"},
           "subtlex.tsv")
    export("ESCOLEX.xlsx", "G1-G6",
           {"Wordform": "word", "FrequencyAbs (FAbs)": "esc_count",
            "Standard frequency index (SFI)": "esc_sfi", "Part-of-Speech (POS)": "esc_pos"},
           "escolex.tsv")
