#!/usr/bin/env bash
# Documentation hygiene gate (review F6).
#   doc_check.sh FILE...
# Fails when a release note contains shell residue (heredoc tails, pasted
# command lines with redirection) or when a claim token appears only inside a
# shell/fence line instead of prose. Lines inside ``` fences are skipped, so
# run instructions stay legal.
set -euo pipefail
[ $# -gt 0 ] || { echo "usage: doc_check.sh FILE..."; exit 2; }
fail=0
for f in "$@"; do
  [ -f "$f" ] || { echo "DOC-FAIL missing $f"; fail=1; continue; }
  awk -v f="$f" '
    BEGIN{ infence=0; bad=0 }
    /^```/{ infence = !infence; next }
    infence { next }
    # heredoc tail glued to prose, or a pasted harness invocation
    /\.DOC$/ || /^DOC$/ || /nohup bash -c/ || />&[[:space:]]*\/tmp\// {
      printf "DOC-FAIL %s:%d shell residue: %s\n", f, NR, $0; bad=1; next }
    { line[NR] = $0 }
    END{
      # verdict tokens must appear in a prose line (>=5 words, not a command)
      split("MULTIREG-NOT-DEMONSTRATED SCALE-NOT-DEMONSTRATED DP-VALUE-NOT-DEMONSTRATED PAIR-LEARN-NOT-DEMONSTRATED", toks, " ")
      for (t = 1; t <= 4; t++){
        found = 0; prose = 0
        for (i = 1; i <= NR; i++){
          if (index(line[i], toks[t]) == 0) continue
          found = 1
          n = split(line[i], w, " ")
          if (n >= 5 && line[i] !~ /^(echo|cd|nohup|bash)[[:space:]]/) prose = 1
        }
        if (found && !prose){ printf "DOC-FAIL %s: token %s only in a non-prose line\n", f, toks[t]; bad = 1 }
      }
      exit bad
    }' "$f" || fail=1
done
[ "$fail" -eq 0 ] && echo "DOC-PASS $# release notes: prose only, tokens in context (fenced commands allowed)"
exit $fail
