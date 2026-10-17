#!/usr/bin/env python3
"""
Extract Wordle word candidate lists from the ESCOLEX corpus (G1-G6 sheet).

Run from this experiment folder:
    python extract_words.py [character_count]   # default: 5

Outputs (written to this folder, LF endings):
    words-valid.txt   All words of the given length (accepted player input)
    words-answer.txt  Filtered list: excludes verb-only words not in infinitive form

The canonical lists at corpus/words-valid.txt and corpus/words-answer.txt
are NOT touched by this script — promote manually (cp to corpus/ and src/data/).
"""

import sys
from pathlib import Path
import pandas as pd


def extract_words(char_count=5):
    script_dir = Path(__file__).resolve().parent
    corpus_path = script_dir / "ESCOLEX.xlsx"

    df = pd.read_excel(corpus_path, sheet_name="G1-G6", usecols=["Wordform", "Part-of-Speech (POS)"])
    df = df.rename(columns={"Part-of-Speech (POS)": "PoS"})

    # Keep only rows where Wordform is a plain alphabetic string of the right length
    df["Wordform"] = df["Wordform"].astype(str).str.strip().str.lower()
    mask_len = df["Wordform"].str.len() == char_count
    mask_alpha = df["Wordform"].str.match(r'^[a-záéíóúâêôãõàüç]+$')
    df = df[mask_len & mask_alpha].copy()

    def write_list(name, words):
        path = script_dir / name
        # newline='\n' guards against Windows text mode rewriting to CRLF
        path.write_text("\n".join(words) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(words)} words")

    # ── valid input list ──────────────────────────────────────────────────────
    valid_words = sorted(df["Wordform"].unique())
    write_list("words-valid.txt", valid_words)

    # ── answer list ───────────────────────────────────────────────────────────
    # Exclude words whose PoS is *exclusively* "V" AND that are NOT infinitives
    infinitive_endings = ("ar", "er", "ir")

    def keep_as_answer(row):
        pos = str(row["PoS"]).strip()
        word = row["Wordform"]
        if pos == "V":
            return word.endswith(infinitive_endings)
        return True

    answer_mask = df.apply(keep_as_answer, axis=1)
    answer_words = sorted(df.loc[answer_mask, "Wordform"].unique())
    write_list("words-answer.txt", answer_words)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    extract_words(count)
