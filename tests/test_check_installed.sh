#!/usr/bin/env bash
# Tests scripts/check-installed.sh in a throw-away HOME: identical, differs, missing, and that it never changes anything.
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
WS="$T/ws"; BIN="$T/bin"; mkdir -p "$WS/theater-router/scripts" "$WS/mpv-object-audio/scripts" "$BIN" "$T/home"
for f in theater-route set-eq.py upmix.py upmix_engine.py; do echo "repo $f" > "$WS/theater-router/scripts/$f"; cp "$WS/theater-router/scripts/$f" "$BIN/$f"; done
for f in mpv-object-audio mpv-atmos; do echo "repo $f" > "$WS/mpv-object-audio/scripts/$f"; cp "$WS/mpv-object-audio/scripts/$f" "$BIN/$f"; done
ln -s theater-route "$BIN/eq"
run() { HOME="$T/home" SDHT_WORKSPACE="$WS" BIN="$BIN" MPVCONF="$T/none" bash "$HERE/scripts/check-installed.sh" "$@" 2>&1; }
fail=0; ck() { if [ "$2" = ok ]; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }
snap() { (cd "$T" && find . -type f -o -type l | sort | xargs -r sha256sum 2>/dev/null; find . -type l -exec readlink {} \;) | sha256sum; }
before=$(snap); out=$(run); rc=$?
ck "everything identical: exit 0 and OK message" "$([ $rc = 0 ] && echo "$out" | grep -q '^OK:' && echo ok)"
echo "changed" >> "$BIN/set-eq.py"
out=$(run); rc=$?
ck "a changed script is reported as DIFFERS with exit 1" "$([ $rc = 1 ] && echo "$out" | grep -q 'set-eq.py *DIFFERS' && echo ok)"
ck "the update command is printed, not run" "$(echo "$out" | grep -q 'install-autoroute.sh' && echo ok)"
out=$(run --diff)
ck "--diff shows the difference" "$(echo "$out" | grep -q '^ *| ' && echo ok)"
rm "$BIN/upmix.py"
out=$(run); rc=$?
ck "a missing script is reported as MISSING" "$(echo "$out" | grep -q 'upmix.py *MISSING' && echo ok)"
rm "$WS/mpv-object-audio/scripts/mpv-atmos"
out=$(run)
ck "a script missing from the repository is reported as NO-REPO" "$(echo "$out" | grep -q 'mpv-atmos *NO-REPO' && echo ok)"
# read-only: restore the two edits we made on purpose, then nothing may differ from the first snapshot
cp "$WS/theater-router/scripts/set-eq.py" "$BIN/set-eq.py"; cp "$WS/theater-router/scripts/upmix.py" "$BIN/upmix.py"; echo "repo mpv-atmos" > "$WS/mpv-object-audio/scripts/mpv-atmos"
run >/dev/null; run --diff >/dev/null
ck "running it (also with --diff) changes no file" "$([ "$(snap)" = "$before" ] && echo ok)"
exit $fail
