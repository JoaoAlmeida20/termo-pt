#!/usr/bin/env bash
# Download every external source into sources/<name>/ (git-ignored, ~600 MB).
# All URLs verified 2026-10-16. Each source lands in its own directory and is
# only ever *read* by the scripts (never executed).
set -euo pipefail
cd "$(dirname "$0")/../sources"

get() {  # get <dir> <url> [output-name]
  mkdir -p "$1"
  local out="$1/${3:-$(basename "$2")}"
  [ -s "$out" ] && { echo "have $out"; return; }
  echo "get  $out"
  curl -sSfL --retry 3 --max-time 900 -o "$out" "$2"
}

LO=https://raw.githubusercontent.com/LibreOffice/dictionaries/master
get hunspell_lo "$LO/pt_PT/pt_PT.dic"; get hunspell_lo "$LO/pt_PT/pt_PT.aff"   # Natura pt_PT AO90 (GPL/LGPL/MPL)
get hunspell_lo "$LO/pt_BR/pt_BR.dic"; get hunspell_lo "$LO/pt_BR/pt_BR.aff"   # VERO pt_BR (LGPLv3/MPL)

FW=https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018
get opensubs "$FW/pt/pt_full.txt"; get opensubs "$FW/pt_br/pt_br_full.txt"      # OpenSubtitles 2018 (CC-BY-SA-4.0)

get wiktionary https://kaikki.org/dictionary/Portuguese/kaikki.org-dictionary-Portuguese.jsonl.gz kaikki-pt.jsonl.gz  # CC BY-SA

get linguateca https://www.linguateca.pt/acesso/tokens/formas.totalpt.txt      # AC/DC (cite Linguateca)
get linguateca https://www.linguateca.pt/acesso/tokens/formas.totalbr.txt

# CLUL server sometimes answers HTTP/0.9 over IPv4; IPv6 works
mkdir -p corlex
[ -s corlex/lmcpc_dec.txt ] || curl -sSfL -6 --retry 3 -o corlex/lmcpc_dec.txt \
  https://clul.ulisboa.pt/sites/default/files/inline-files/lmcpc_dec.txt

NAT=https://natura.di.uminho.pt/download/sources/Dictionaries/wordlists/LATEST
get natura "$NAT/wordlist-ao-latest.txt.xz" wordlist-ao.txt.xz
get natura "$NAT/wordlist-preao-latest.txt.xz" wordlist-preao.txt.xz

LZ=https://downloads.wortschatz-leipzig.de/corpora
for n in por-pt_newscrawl_2011_300K por-br_newscrawl_2011_300K por-pt_web_2015_300K; do
  get leipzig "$LZ/$n.tar.gz"
done

LT=https://raw.githubusercontent.com/languagetool-org/languagetool/master/languagetool-language-modules/pt/src/main/resources/org/languagetool
get languagetool "$LT/resource/pt/dialect_alternations.txt"                      # held-out BR=PT test pairs (LGPL)
