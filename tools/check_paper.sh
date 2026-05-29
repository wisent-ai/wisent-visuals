#!/usr/bin/env bash
# check_paper.sh — pre-submission preflight for a LaTeX paper.
#
# Usage: check_paper.sh <path/to/main.tex>
#
# Runs a clean pdflatex+bibtex+pdflatex+pdflatex build, then evaluates a set of
# HARD checks (nonzero exit if any fail) and SOFT checks (reported only). It was
# written after the RepScan paper shipped with a broken build, duplicate bib
# entries, ~85 undefined citations, and fabricated-result stubs — every one of
# which a hard check below would have caught.
#
# Hard (fail the submission): LaTeX errors, undefined citations, undefined
#   references, multiply-defined labels, duplicate bib entries, placeholder /
#   fabrication markers (XXX, TODO, TBD, placeholder, lorem, Rephrased:, empty
#   \cite{}, empty \textbf{}).
# Soft (reported): page count, overfull hboxes, figure labels never referenced,
#   chktex and lacheck warning counts.
#
# Counting uses awk (not `wc`, which is shadowed by the wisent-compute CLI on
# some machines). No network, no compute; fully local.

set -u
MAIN="${1:-}"
[ -n "$MAIN" ] || { echo "usage: check_paper.sh <main.tex>"; exit 2; }
[ -f "$MAIN" ] || { echo "FAIL: '$MAIN' not found"; exit 2; }
DIR=$(cd "$(dirname "$MAIN")" && pwd)
BASE=$(basename "$MAIN" .tex)
cd "$DIR" || exit 2

countlines(){ awk 'END{print NR+0}'; }            # stdin -> line count (no wc)
fail=0
HARD(){ if [ "$2" -ne 0 ]; then echo "  [FAIL] $1"; fail=1; else echo "  [ ok ] $1"; fi; }

# Resolve the source files to scan: main + any \input/\include targets.
srcfiles(){
  echo "$BASE.tex"
  awk '{ s=$0; while(match(s,/\\(input|include)\{[^}]+\}/)){ t=substr(s,RSTART,RLENGTH); sub(/^\\(input|include)\{/,"",t); sub(/\}$/,"",t); if(t !~ /\.tex$/) t=t".tex"; print t; s=substr(s,RSTART+RLENGTH) } }' "$BASE.tex" 2>/dev/null
}

echo "== build: $BASE.tex (clean pdflatex -> bibtex -> pdflatex x2) =="
rm -f "$BASE.aux" "$BASE.bbl" "$BASE.blg" "$BASE.log" 2>/dev/null
pdflatex -interaction=nonstopmode "$BASE.tex" >/dev/null 2>&1
bibtex "$BASE" >/dev/null 2>&1
pdflatex -interaction=nonstopmode "$BASE.tex" >/dev/null 2>&1
pdflatex -interaction=nonstopmode "$BASE.tex" >/dev/null 2>&1
LOG="$BASE.log"; BLG="$BASE.blg"
[ -f "$LOG" ] || { echo "FAIL: build produced no $LOG (pdflatex did not run)"; exit 2; }

echo "== HARD checks =="
NE=$(awk '/^! /{c++}END{print c+0}' "$LOG")
HARD "LaTeX errors: $NE" "$NE"

UC=$(awk -F"[\140\047]" '/Citation/ && /undefined/{print $2}' "$LOG" | sort -u | countlines)
HARD "undefined citations: $UC" "$UC"
[ "$UC" -ne 0 ] && echo "         -> $(awk -F"[\140\047]" '/Citation/ && /undefined/{print $2}' "$LOG" | sort -u | tr '\n' ' ')"

UR=$(awk -F"[\140\047]" '/Reference/ && /undefined/{print $2}' "$LOG" | sort -u | countlines)
HARD "undefined references: $UR" "$UR"
[ "$UR" -ne 0 ] && echo "         -> $(awk -F"[\140\047]" '/Reference/ && /undefined/{print $2}' "$LOG" | sort -u | tr '\n' ' ')"

MD=$(awk '/multiply defined/{c++}END{print c+0}' "$LOG")
HARD "multiply-defined labels: $MD" "$MD"

DUP=0
[ -f "$BLG" ] && DUP=$(awk '/Repeated entry/{c++}END{print c+0}' "$BLG")
HARD "duplicate bib entries: $DUP" "$DUP"
[ "$DUP" -ne 0 ] && echo "         -> $(awk '/Repeated entry/{print}' "$BLG" | tr '\n' ' ')"

PLC=0
for f in $(srcfiles); do
  [ -f "$f" ] || continue
  n=$(awk '/XXX|\<TODO\>|\<TBD\>|placeholder|[Ll]orem ipsum|Rephrased:|\\cite\{\}|\\textbf\{\}/{c++}END{print c+0}' "$f")
  PLC=$((PLC+n))
done
HARD "placeholder/fabrication markers: $PLC" "$PLC"

echo "== SOFT checks (reported) =="
PAGES=$(pdfinfo "$BASE.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
echo "  pages: ${PAGES:-?}"
OFB=$(awk '/Overfull \\hbox/{c++}END{print c+0}' "$LOG")
echo "  overfull hboxes: $OFB"

# figure labels defined but never \ref'd (possible orphan figures)
ALLSRC=$(for f in $(srcfiles); do [ -f "$f" ] && cat "$f"; done)
ORPH=$(printf '%s\n' "$ALLSRC" | awk '
  { s=$0; while(match(s,/\\label\{fig:[^}]+\}/)){ t=substr(s,RSTART,RLENGTH); sub(/^\\label\{/,"",t); sub(/\}$/,"",t); lab[t]=1; s=substr(s,RSTART+RLENGTH) } }
  { s=$0; while(match(s,/\\ref\{fig:[^}]+\}/)){ t=substr(s,RSTART,RLENGTH); sub(/^\\ref\{/,"",t); sub(/\}$/,"",t); ref[t]=1; s=substr(s,RSTART+RLENGTH) } }
  END{for(l in lab) if(!(l in ref)) print l}')
if [ -n "$ORPH" ]; then echo "  figure labels never referenced: $(printf '%s' "$ORPH" | tr '\n' ' ')"; else echo "  figure labels never referenced: none"; fi

command -v chktex  >/dev/null 2>&1 && echo "  chktex warnings:  $(chktex -q "$BASE.tex" 2>/dev/null | countlines)"
command -v lacheck >/dev/null 2>&1 && echo "  lacheck warnings: $(lacheck "$BASE.tex" 2>/dev/null | countlines)"

echo "== verdict =="
if [ "$fail" -eq 0 ]; then echo "PASS — submission preflight clean"; exit 0; else echo "FAIL — resolve the [FAIL] items above before submitting"; exit 1; fi
