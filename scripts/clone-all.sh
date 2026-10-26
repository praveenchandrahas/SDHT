#!/usr/bin/env bash
# Clones (or updates) every repository of the software-defined home theatre into one folder, side by side.
#   ./scripts/clone-all.sh [TARGET_FOLDER]      default: the folder that contains this repository
# The repositories find each other by folder name (or by SDHT_WORKSPACE), so keep the names.
set -e
OWNER="${SDHT_OWNER:-praveenchandrahas}"
HERE=$(cd "$(dirname "$0")/.." && pwd)
TARGET="${1:-$(dirname "$HERE")}"
mkdir -p "$TARGET"
for r in SDHT linux-theater-dsp mpv-object-audio seekthumbs theater-measurement; do
  if [ "${r,,}" = "$(basename "$HERE" | tr A-Z a-z)" ] || [ -d "$TARGET/$r/.git" ]; then
    d="$TARGET/$r"; [ "${r,,}" = "$(basename "$HERE" | tr A-Z a-z)" ] && d="$HERE"
    echo "== $r: updating"; git -C "$d" pull --ff-only || echo "   (could not fast-forward; left as is)"
  else
    echo "== $r: cloning"; git clone "https://github.com/$OWNER/$r" "$TARGET/$r"
  fi
done
echo "Done. Repositories are in $TARGET. Next: scripts/test-all.sh"
