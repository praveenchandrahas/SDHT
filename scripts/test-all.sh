#!/usr/bin/env bash
# Runs the test suite of every sibling repository that is present (no hardware needed). Needs python3 with PyYAML, numpy, scipy, and ffmpeg for seekthumbs.
HERE=$(cd "$(dirname "$0")/.." && pwd)
WS="${SDHT_WORKSPACE:-$(dirname "$HERE")}"
rc=0
for r in linux-theater-dsp mpv-object-audio seekthumbs theater-measurement; do
  if [ -f "$WS/$r/tests/run.sh" ]; then
    echo "== $r"; bash "$WS/$r/tests/run.sh" || { echo "FAIL: $r tests failed"; rc=1; }
  else
    echo "== $r: not found in $WS (scripts/clone-all.sh)"
  fi
done
exit $rc
