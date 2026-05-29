#!/usr/bin/env bash
# build_neurips_profile.sh — build the empirical norm profile for
# check_neurips_paper.sh from NeurIPS/ICML/ICLR award/oral/spotlight papers.
#
# For each curated paper TITLE it resolves an arXiv id via the public arXiv
# export API, downloads the PDF, and parses page count, reference count, figure
# count, table count, and section presence. It then writes a norm profile
# (per-metric min/median/max and per-section frequency) to:
#   tools/neurips_profile.json
#
# Usage: build_neurips_profile.sh        (re-downloads + reparses everything)
# Public award papers only; read-only scraping; no credentials, no compute.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/.neurips_corpus"
mkdir -p "$WORK"
OUT="$HERE/neurips_profile.json"

# Curated award / oral / spotlight papers, NeurIPS+ICML+ICLR 2023-2025.
TITLES=(
"Visual Autoregressive Modeling: Scalable Image Generation via Next-Scale Prediction"
"Stochastic Taylor Derivative Estimator: Efficient amortization for arbitrary differential operators"
"Not All Tokens Are What You Need for Pretraining"
"Guiding a Diffusion Model with a Bad Version of Itself"
"Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution"
"Measure Dataset Diversity, Don't Just Claim It"
"Debating with More Persuasive LLMs Leads to More Truthful Answers"
"Generalization in diffusion models arises from geometry-adaptive harmonic representations"
"Learning Interactive Real-World Simulators"
"Never Train from Scratch: Fair Comparison of Long-Sequence Models Requires Data-Driven Priors"
"Protein Discovery with Discrete Walk-Jump Sampling"
"Vision Transformers Need Registers"
"Amortizing intractable inference in large language models"
"Beyond Weisfeiler-Lehman: A Quantitative Framework for GNN Expressiveness"
"Flow Matching on General Geometries"
"Model Tells You What to Discard: Adaptive KV Cache Compression for LLMs"
"Proving Test Set Contamination in Black-Box Language Models"
"Robust agents learn causal world models"
"Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
"Are Emergent Abilities of Large Language Models a Mirage?"
)

urlenc(){ jq -rn --arg t "$1" '$t|@uri'; }

echo "== resolving + downloading ${#TITLES[@]} award papers =="
i=0
for t in "${TITLES[@]}"; do
  i=$((i+1)); id="$WORK/p$i"
  pdf="$id.pdf"
  q=$(urlenc "$t")
  aid=$(curl -sL "https://export.arxiv.org/api/query?search_query=ti:%22$q%22&max_results=1" 2>/dev/null \
        | awk 'match($0,/<id>http[s]?:\/\/arxiv\.org\/abs\/([^<]+)<\/id>/){print substr($0,RSTART,RLENGTH); exit}' \
        | sed -E 's#.*/abs/##; s#</id>##')
  [ -n "$aid" ] && printf '%s' "${aid%v[0-9]*}" > "$id.aid"
  if [ ! -s "$pdf" ]; then
    [ -z "$aid" ] && { echo "  [miss] $t"; continue; }
    curl -sL "https://arxiv.org/pdf/$aid" -o "$pdf" 2>/dev/null
  fi
  [ -s "$pdf" ] || { echo "  [dlfail] $t"; continue; }
  # Also fetch the LaTeX SOURCE (e-print tarball) — per-section lengths are read
  # from \section boundaries in the source, which is exact, unlike PDF text where
  # headers are letter-spaced/merged.
  if [ ! -d "$id.srcd" ] && [ -n "$aid" ]; then
    curl -sL "https://arxiv.org/e-print/$aid" -o "$id.src" 2>/dev/null
    mkdir -p "$id.srcd"
    tar xzf "$id.src" -C "$id.srcd" 2>/dev/null || gunzip -c "$id.src" > "$id.srcd/main.tex" 2>/dev/null
  fi
  echo "  [ok] p$i $(basename "$pdf")"
done

echo "== parsing =="
ROWS="$WORK/rows.tsv"; : > "$ROWS"
for pdf in "$WORK"/p*.pdf; do
  [ -s "$pdf" ] || continue
  pages=$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  txt="${pdf%.pdf}.txt"
  pdftotext "$pdf" "$txt" 2>/dev/null
  [ -f "$txt" ] || continue
  figs=$(awk 'BEGIN{m=0}/^Figure [0-9]+[:.]/{n=$2+0; if(n>m)m=n}END{print m}' "$txt")
  tabs=$(awk 'BEGIN{m=0}/^Table [0-9]+[:.]/{n=$2+0; if(n>m)m=n}END{print m}' "$txt")
  # (reference COUNT norms are intentionally NOT scraped: counting refs from
  #  2-column / author-year PDFs is unreliable, and the Semantic Scholar API
  #  rate-limits unauthenticated bulk lookups. check_neurips_paper.sh instead
  #  counts the TARGET paper's references from its .bbl and compares to a fixed
  #  advisory bar.)
  # main-body vs back-matter split: the page where the References header starts
  # is the end of the main body. NeurIPS-style headers are letter-spaced
  # ("R EFERENCES"), so compare de-spaced+lowered. Form feeds (\f) delimit pages.
  # has_appendix: an Appendix/Supplementary header after refs, or back matter too
  # long to be references alone (refs rarely exceed ~6 pages).
  mba=$(awk 'BEGIN{pg=1;refpg=0;mk=0}
    { n=gsub(/\f/,"\f"); line=$0; gsub(/\f/,"",line); d=line; gsub(/ /,"",d); dl=tolower(d);
      if(refpg==0 && dl=="references") refpg=pg;
      if(mk==0 && (dl ~ /^appendix/||dl ~ /^supplementary/) && refpg>0 && pg>=refpg) mk=pg;
      pg+=n }
    END{ back=(refpg>0?pg-refpg:0); hasapp=((mk>0)||(back>=7))?1:0; print (refpg>0?refpg:0)" "back" "hasapp }' "$txt")
  mb=${mba%% *}; rest=${mba#* }; bk=${rest%% *}; app=${rest##* }
  # section presence (1/0)
  sec(){ awk -v p="$1" 'BEGIN{IGNORECASE=1} index(tolower($0),p){f=1} END{print f+0}' "$txt"; }
  rw=$(sec "related work"); ex=$(sec "experiment"); ab=$(sec "ablation"); lim=$(sec "limitation"); concl=$(sec "conclusion"); repro=$(sec "reproducib"); impact=$(sec "broader impact")
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "${pages:-0}" "${figs:-0}" "${tabs:-0}" "$rw" "$ex" "$ab" "$lim" "$concl" "$repro" "$impact" "${mb:-0}" "${bk:-0}" "${app:-0}" >> "$ROWS"
done

echo "== section + appendix words (arXiv source: \\section boundaries) =="
SECROWS="$WORK/secrows.tsv"; : > "$SECROWS"
# Expand \input/\include IN PLACE (preserve order) so \appendix correctly splits
# main body from appendix; appending includes at the end mis-segments papers that
# \input their body sections (RSTART/RLENGTH captured into locals because nested
# match() in emit() clobbers the globals). Two levels covers sections/all.tex.
expand_tex(){ awk -v DIR="$2" '
    function emit(fn,lvl,  path,l,rs,rl,t){ if(fn !~ /\.tex$/) fn=fn".tex"; path=DIR"/"fn;
      while((getline l < path)>0){
        if(lvl<2 && match(l,/\\(input|include)\{[^}]+\}/)){ rs=RSTART; rl=RLENGTH; printf "%s\n", substr(l,1,rs-1);
          t=substr(l,rs,rl); sub(/^\\(input|include)\{/,"",t); sub(/\}.*/,"",t); emit(t,lvl+1); print substr(l,rs+rl) }
        else print l }
      close(path) }
    /\\(input|include)\{[^}]+\}/ { line=$0;
      while(match(line,/\\(input|include)\{[^}]+\}/)){ rs=RSTART; rl=RLENGTH; printf "%s\n", substr(line,1,rs-1);
        t=substr(line,rs,rl); sub(/^\\(input|include)\{/,"",t); sub(/\}.*/,"",t); emit(t,1); line=substr(line,rs+rl) } print line; next }
    { print }' "$1"; }
for d in "$WORK"/p*.srcd; do
  [ -d "$d" ] || continue
  main=""
  for tx in "$d"/*.tex; do [ -f "$tx" ] || continue; if awk '/\\begin\{document\}/{f=1}END{exit !f}' "$tx"; then main="$tx"; break; fi; done
  [ -n "$main" ] || continue
  expand_tex "$main" "$d" | awk '
    function mbucket(n,  l){ l=tolower(n);
      if(l ~ /introduction/) return "introduction";
      if(l ~ /related|prior work/) return "related_work";
      if(l ~ /experiment|empirical|evaluation|results/) return "experiments";
      if(l ~ /conclusion|discussion/) return "conclusion"; return "" }
    function abucket(n,  l){ l=tolower(n);
      if(l ~ /proof|derivation|lemma|theorem/) return "proofs";
      if(l ~ /implementation|experimental detail|training detail|hyperparam|setup|architecture/) return "implementation_details";
      if(l ~ /additional|extended|further|qualitative|more result|ablation/) return "additional_results";
      if(l ~ /reproducib|checklist/) return "reproducibility_checklist";
      if(l ~ /broader impact|societal|ethic/) return "broader_impact"; return "" }
    function isapp(n,  l){ l=tolower(n); return (l ~ /^appendix|supplementary/) }
    function isback(n,  l){ l=tolower(n); return (l ~ /references|acknowledg|author contribution/) }
    function flush(   b,c){ if(cur!=""){
        if(!inapp){ b=mbucket(cur); if(b!="") print "BUK\t"b"\t"w }
        else if(appmode){ acount++; awords+=w; c=abucket(cur); if(c!=""&&!seen[c]){seen[c]=1; print "APXC\t"c} } } }
    /\\appendix([^a-zA-Z]|$)/ { flush(); inapp=1; appmode=1; cur=""; w=0; next }
    /\\section\*?\{/ { flush(); s=$0; match(s,/\\section\*?\{[^}]*\}/); h=substr(s,RSTART,RLENGTH); sub(/\\section\*?\{/,"",h); sub(/\}.*/,"",h);
      if(isapp(h)){appmode=1; inapp=1} else if(isback(h)){inapp=1} cur=h; w=0; next }
    cur!="" { t=$0; gsub(/%.*/,"",t); gsub(/\\[a-zA-Z]+\*?/,"",t); gsub(/[{}$&~^_]/," ",t); w+=split(t,a," ") }
    END{ flush(); if(acount>0) print "APXS\t"acount"\t"awords }' >> "$SECROWS"
done
medb(){ awk -F'\t' -v B="$1" '$1=="BUK"&&$2==B{a[++n]=$3} END{ for(i=1;i<=n;i++)for(j=i+1;j<=n;j++)if(a[j]<a[i]){t=a[i];a[i]=a[j];a[j]=t} print (n?((n%2)?a[int(n/2)+1]:int((a[n/2]+a[n/2+1])/2)):0)" "(n+0) }' "$SECROWS"; }
xi=$(medb introduction); xr=$(medb related_work); xe=$(medb experiments); xc=$(medb conclusion)
SECJSON=$(printf '{"introduction":{"median_words":%s,"n":%s},"related_work":{"median_words":%s,"n":%s},"experiments":{"median_words":%s,"n":%s},"conclusion":{"median_words":%s,"n":%s}}' \
  "${xi% *}" "${xi#* }" "${xr% *}" "${xr#* }" "${xe% *}" "${xe#* }" "${xc% *}" "${xc#* }")
napx=$(awk -F'\t' '$1=="APXS"{n++}END{print n+0}' "$SECROWS")
medcol(){ awk -F'\t' -v C="$1" '$1=="APXS"{a[++n]=$C} END{ for(i=1;i<=n;i++)for(j=i+1;j<=n;j++)if(a[j]<a[i]){t=a[i];a[i]=a[j];a[j]=t} print (n?((n%2)?a[int(n/2)+1]:int((a[n/2]+a[n/2+1])/2)):0) }' "$SECROWS"; }
asec=$(medcol 2); awrd=$(medcol 3)
cfreq(){ awk -F'\t' -v C="$1" -v N="$napx" '$1=="APXC"&&$2==C{c++} END{printf "%.2f", (N>0?c/N:0)}' "$SECROWS"; }
APXJSON=$(printf '{"n_with_appendix":%s,"median_sections":%s,"median_words":%s,"component_freq":{"proofs":%s,"implementation_details":%s,"additional_results":%s,"reproducibility_checklist":%s,"broader_impact":%s}}' \
  "${napx:-0}" "${asec:-0}" "${awrd:-0}" "$(cfreq proofs)" "$(cfreq implementation_details)" "$(cfreq additional_results)" "$(cfreq reproducibility_checklist)" "$(cfreq broader_impact)")
echo "  sections: $SECJSON"
echo "  appendix: $APXJSON"

N=$(awk 'END{print NR+0}' "$ROWS")
echo "== aggregating $N parsed papers -> $OUT =="
awk -v n="$N" '
  function stats(arr, c,   i,j,t,med){ for(i=1;i<=c;i++)for(j=i+1;j<=c;j++)if(arr[j]<arr[i]){t=arr[i];arr[i]=arr[j];arr[j]=t}
    med=(c%2)?arr[int(c/2)+1]:int((arr[c/2]+arr[c/2+1])/2); return arr[1]"|"med"|"arr[c] }
  { pg[NR]=$1; fg[NR]=$2; tb[NR]=$3; rw+=$4; ex+=$5; ab+=$6; lim+=$7; cc+=$8; rp+=$9; im+=$10; mb[NR]=$11; bk[NR]=$12; app+=$13 }
  END{
    sp=stats(pg,NR); sf=stats(fg,NR); st=stats(tb,NR); smb=stats(mb,NR); sbk=stats(bk,NR)
    split(sp,a,"|"); split(sf,b,"|"); split(st,c,"|"); split(smb,d,"|"); split(sbk,e,"|")
    printf "{\n  \"n_papers\": %d,\n", NR
    printf "  \"pages\":   {\"min\": %s, \"median\": %s, \"max\": %s},\n", a[1],a[2],a[3]
    printf "  \"main_body_pages\":   {\"min\": %s, \"median\": %s, \"max\": %s},\n", d[1],d[2],d[3]
    printf "  \"back_matter_pages\": {\"min\": %s, \"median\": %s, \"max\": %s},\n", e[1],e[2],e[3]
    printf "  \"has_appendix_frac\": %.2f,\n", app/NR
    printf "  \"figures\": {\"min\": %s, \"median\": %s, \"max\": %s},\n", b[1],b[2],b[3]
    printf "  \"tables\":  {\"min\": %s, \"median\": %s, \"max\": %s},\n", c[1],c[2],c[3]
    printf "  \"section_freq\": {\"related_work\": %.2f, \"experiments\": %.2f, \"ablation\": %.2f, \"limitations\": %.2f, \"conclusion\": %.2f, \"reproducibility\": %.2f, \"broader_impact\": %.2f}\n",
           rw/NR, ex/NR, ab/NR, lim/NR, cc/NR, rp/NR, im/NR
    printf "}\n"
  }' "$ROWS" > "$OUT.tmp"
jq --argjson sw "$SECJSON" --argjson ax "$APXJSON" '. + {section_words: $sw, appendix: $ax}' "$OUT.tmp" > "$OUT" && rm -f "$OUT.tmp"
cat "$OUT"
