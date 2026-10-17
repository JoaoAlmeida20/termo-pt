#!/usr/bin/env python3
"""
Extract Wordle word candidate lists from SUBTLEX-PT corpus.

Usage:
    python extract_words.py [character_count]

Arguments:
    character_count   Number of letters (default: 5)

Outputs:
    words-valid.txt   All words of the given length (accepted player input)
    words-answer.txt  Filtered list: excludes verb-only words not in infinitive form
"""

import sys
import re
import pandas as pd

def extract_words(char_count=5):
    corpus_path = "subtlex_pt.xlsx"

    df = pd.read_excel(corpus_path, sheet_name="SUBTLEX-PT", usecols=["Wordform", "PoS"])

    # Keep only rows where Wordform is a plain alphabetic string of the right length
    df["Wordform"] = df["Wordform"].astype(str).str.strip().str.lower()
    mask_len = df["Wordform"].str.len() == char_count
    mask_alpha = df["Wordform"].str.match(r'^[a-záéíóúâêôãõàüç]+$')
    df = df[mask_len & mask_alpha].copy()

    # ── valid input list ──────────────────────────────────────────────────────
    valid_words = sorted(df["Wordform"].unique())
    with open("words-valid.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid_words) + "\n")
    print(f"words-valid.txt: {len(valid_words)} words")

    # ── answer list ───────────────────────────────────────────────────────────
    # Exclude words whose PoS is *exclusively* "V" AND that are NOT infinitives
    infinitive_endings = ("ar", "er", "ir")

    def keep_as_answer(row):
        pos = str(row["PoS"]).strip()
        word = row["Wordform"]
        # If PoS is only "V" (no other tags), apply the infinitive filter
        if pos == "V":
            return word.endswith(infinitive_endings)
        return True

    answer_mask = df.apply(keep_as_answer, axis=1)
    answer_words = sorted(df.loc[answer_mask, "Wordform"].unique())

    with open("words-answer.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(answer_words) + "\n")
    print(f"words-answer.txt: {len(answer_words)} words")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    extract_words(count)
