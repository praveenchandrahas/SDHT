#!/usr/bin/env bash
# Compares what is INSTALLED on this machine with the copies in the repositories. READ-ONLY:
#   - it only reads files (cmp, readlink, git status); it writes nothing, installs nothing, deletes nothing, uses no network and no sudo;
#   - when something differs it PRINTS the command you would run to update it. You decide whether to run it.
# Usage:  scripts/check-installed.sh [--diff]        --diff also shows the differences
# Exit status: 0 = everything identical, 1 = something differs or is missing.
# Folders: the repositories side by side (SDHT_WORKSPACE overrides), installed scripts in BIN (default ~/.local/bin), mpv config in MPVCONF.
HERE=$(cd "$(dirname "$0")/.." && pwd)
WS="${SDHT_WORKSPACE:-$(dirname "$HERE")}"
BIN="${BIN:-$HOME/.local/bin}"
MPVCONF="${MPVCONF:-$HOME/.config/mpv-object-audio}"
SHOWDIFF=0; [ "${1:-}" = "--diff" ] && SHOWDIFF=1
bad=0; n=0
row() {   # row LABEL INSTALLED REPOFILE UPDATE-HINT
  local label=$1 inst=$2 repo=$3 hint=$4
  n=$((n + 1))
  if [ ! -f "$repo" ]; then printf '%-24s NO-REPO   (repository file not found: %s)\n' "$label" "$repo"; bad=1; return; fi
  if [ ! -e "$inst" ]; then printf '%-24s MISSING    (not installed: %s)\n             to install: %s\n' "$label" "$inst" "$hint"; bad=1; return; fi
  if cmp -s "$inst" "$repo"; then printf '%-24s identical\n' "$label"
  else
    printf '%-24s DIFFERS    (%s)\n             to update: %s\n' "$label" "$inst" "$hint"; bad=1
    [ "$SHOWDIFF" = 1 ] && diff -u "$inst" "$repo" | head -40 | sed 's/^/             | /'
  fi
}
R="$WS/linux-theater-dsp/scripts"; M="$WS/mpv-object-audio/scripts"
UP="cd $WS/linux-theater-dsp && ./scripts/install-autoroute.sh"
row theater-route        "$BIN/theater-route"      "$R/theater-route"      "$UP"
row set-eq.py            "$BIN/set-eq.py"          "$R/set-eq.py"          "$UP"
row upmix.py             "$BIN/upmix.py"           "$R/upmix.py"           "$UP"
row upmix_engine.py      "$BIN/upmix_engine.py"    "$R/upmix_engine.py"    "$UP"
row mpv-object-audio     "$BIN/mpv-object-audio"   "$M/mpv-object-audio"   "cd $WS/mpv-object-audio && ./scripts/object-audio-install.sh"
row mpv-atmos            "$BIN/mpv-atmos"          "$M/mpv-atmos"          "install -m 755 $M/mpv-atmos $BIN/mpv-atmos   (this wrapper is hand-installed; compare it first with --diff)"
if [ -e "$BIN/eq" ]; then
  n=$((n + 1)); if [ "$(readlink "$BIN/eq" 2>/dev/null)" = "theater-route" ]; then printf '%-24s identical    (symlink to theater-route)\n' "eq"; else printf '%-24s DIFFERS    (not a symlink to theater-route)\n' "eq"; bad=1; fi
fi
[ -f "$WS/seekthumbs/thumbfast.lua" ] && [ -e "$MPVCONF/scripts/thumbfast.lua" ] && row "seekthumbs viewer" "$MPVCONF/scripts/thumbfast.lua" "$WS/seekthumbs/thumbfast.lua" "cd $WS/seekthumbs && ./seekthumbs.py install-viewer"
echo
echo "repository state (local only, no network):"
for r in UMBRELLA linux-theater-dsp mpv-object-audio seekthumbs theater-measurement; do
  d="$WS/$r"; [ "$r" = UMBRELLA ] && d="$HERE"
  if [ -d "$d/.git" ]; then
    dirty=$(git -C "$d" status --porcelain 2>/dev/null | wc -l)
    printf '  %-20s %s  %s%s\n' "$([ "$r" = UMBRELLA ] && basename "$HERE" || echo "$r")" "$(git -C "$d" log -1 --format='%h %cs' 2>/dev/null)" "$([ "$dirty" -gt 0 ] && echo "$dirty uncommitted change(s)" || echo clean)" "$(git -C "$d" status -sb 2>/dev/null | head -1 | grep -oE '\[(ahead|behind)[^]]*\]' | sed 's/^/  /')"
  else
    printf '  %-20s not found in %s\n' "$r" "$WS"
  fi
done
echo
if [ "$bad" = 0 ]; then echo "OK: $n item(s) checked, everything installed matches the repositories."; else echo "ATTENTION: something differs or is missing (see above). Nothing was changed."; fi
exit $bad
