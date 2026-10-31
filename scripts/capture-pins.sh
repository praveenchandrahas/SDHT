#!/usr/bin/env bash
# capture-pins.sh: print the sha256, size, date and version of the installed player parts, as a block to paste into
# docs/rebuild-checklist.md (section "Pins recorded on the rig").
#
# READ-ONLY. It writes no file, installs nothing, changes no setting, uses no network and opens no listener.
# It only runs: sha256sum, stat, strings, grep, and "--version" on mpv and CamillaDSP.
# Run it once on the laptop, ideally while no film is playing:   scripts/capture-pins.sh
# Paths are the ones on the author's laptop. Override with the variables below if they differ.
set -u

OMNI="${OMNI:-$HOME/HomeTheatre/Omniphony/mpv-omniphony-v0.4.2-linux-x86_64}"
LIBORENDER_USER="${LIBORENDER_USER:-$HOME/.local/share/omniphony/lib/liborender.so.0}"
LIBORENDER_STUDIO="${LIBORENDER_STUDIO:-/usr/lib/Omniphony Studio/engine/liborender.so.0}"
BRIDGE_MPV="${BRIDGE_MPV:-$OMNI/libharletty_bridge.so}"
BRIDGE_USER="${BRIDGE_USER:-$HOME/.local/share/omniphony/lib/libharletty_bridge.so}"
BRIDGE_CONFIG="${BRIDGE_CONFIG:-$HOME/HomeTheatre/Omniphony/libharletty_bridge.so}"
MPV_BIN="${MPV_BIN:-$OMNI/mpv-omniphony/build/mpv-v0.41.0/_b/mpv}"
MPV_ATMOS="${MPV_ATMOS:-$HOME/.local/bin/mpv-atmos}"
CAMILLA="${CAMILLA:-/usr/local/bin/camilladsp}"
OA_VERSIONS="${OA_VERSIONS:-$HOME/.local/opt/mpv-object-audio/VERSIONS}"

have() { command -v "$1" >/dev/null 2>&1; }

# file_pin LABEL PATH : sha256, size in bytes, modification date
file_pin() {
  local label=$1 path=$2
  if [ ! -f "$path" ]; then
    printf '%-26s MISSING  %s\n' "$label" "$path"
    return
  fi
  printf '%-26s %s\n' "$label" "$path"
  printf '    sha256  %s\n' "$(sha256sum -- "$path" | cut -d' ' -f1)"
  printf '    size    %s bytes\n' "$(stat -c %s -- "$path")"
  printf '    date    %s\n' "$(stat -c %y -- "$path" | cut -c1-16)"
}

# lib_strings PATH : the few version strings a Rust library embeds (bridge API, abi_stable, rustc)
lib_strings() {
  local path=$1
  [ -f "$path" ] || return 0
  if have strings; then
    strings -n 5 -- "$path" 2>/dev/null |
      grep -a -o -E 'bridge_api;[0-9.]+|abi_stable;[0-9.]+|rustc version [0-9.]+ \([^)]*\)' |
      sort -u | head -6 | sed 's/^/    string  /'
  else
    printf '    string  (strings not installed: sudo apt install binutils)\n'
  fi
}

# version_of LABEL BINARY : first line of "BINARY --version", or a note
version_of() {
  local label=$1 bin=$2
  if [ ! -x "$bin" ]; then
    printf '%-26s not found or not executable: %s\n' "$label" "$bin"
    return
  fi
  printf '%-26s %s\n' "$label" "$(timeout 8 "$bin" --version 2>&1 | head -1)"
}

echo '```'
echo "# capture-pins.sh  $(date '+%F %T %Z')  host $(hostname)"
echo "# kernel $(uname -sr)"
if [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  echo "# os     ${PRETTY_NAME:-unknown}"
fi
echo

echo "== Versions =="
have pipewire && printf '%-26s %s\n' "pipewire" "$(pipewire --version 2>&1 | tail -1)"
have wireplumber && printf '%-26s %s\n' "wireplumber" "$(wireplumber --version 2>&1 | tail -1)"
version_of "camilladsp" "$CAMILLA"
version_of "mpv-omniphony (patched)" "$MPV_BIN"
if have dpkg-query; then
  printf '%-26s %s\n' "omniphony-studio (deb)" "$(dpkg-query -W -f='${Version}' omniphony-studio 2>/dev/null || echo 'not a deb package')"
fi
echo

echo "== sha256, size, date =="
file_pin "liborender (mpv loads)" "$LIBORENDER_USER"
lib_strings "$LIBORENDER_USER"
file_pin "liborender (Studio)" "$LIBORENDER_STUDIO"
lib_strings "$LIBORENDER_STUDIO"
file_pin "bridge (next to mpv)" "$BRIDGE_MPV"
lib_strings "$BRIDGE_MPV"
file_pin "bridge (~/.local copy)" "$BRIDGE_USER"
file_pin "bridge (omniphony cfg)" "$BRIDGE_CONFIG"
file_pin "mpv binary" "$MPV_BIN"
file_pin "mpv-atmos wrapper" "$MPV_ATMOS"
file_pin "camilladsp binary" "$CAMILLA"
echo

echo "== Which bridge does mpv-atmos pass? =="
if [ -f "$MPV_ATMOS" ]; then
  grep -n -E 'ad-orender-(library|bridge-path)' -- "$MPV_ATMOS" | sed 's/^/    /'
else
  echo "    (no wrapper at $MPV_ATMOS)"
fi
echo

echo "== mpv-object-audio (current player), VERSIONS file =="
if [ -f "$OA_VERSIONS" ]; then
  head -40 -- "$OA_VERSIONS" | sed 's/^/    /'
else
  echo "    (not found: $OA_VERSIONS)"
fi
echo '```'
