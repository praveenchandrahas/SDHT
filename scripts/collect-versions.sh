#!/usr/bin/env bash
# Collects the versions and configuration the README's "Still to fill in" list asks for, into one Markdown report.
# Read-only: it changes nothing. Run it on the theatre laptop, ideally while an Atmos film is playing (the last section reads the live links):
#
#   ./scripts/collect-versions.sh                 # writes ./sdht-versions-YYYY-MM-DD.md and prints it
#   ./scripts/collect-versions.sh --redact        # replaces your user name, home directory and host name with placeholders
#   ./scripts/collect-versions.sh -o report.md    # choose the output file
#
# Then look the report over (mpv.conf can hold media-library paths, share names or passwords), and send it back or paste it into
# docs/installation.md. Nothing is sent anywhere by this script.
set -u
REDACT=0; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --redact) REDACT=1 ;;
    -o) shift; OUT="${1:-}" ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$OUT" ] || OUT="sdht-versions-$(date +%F).md"

have() { command -v "$1" >/dev/null 2>&1; }
h()    { printf '\n## %s\n\n' "$*"; }
code() { printf '```\n'; cat; printf '```\n'; }
run()  { # run "label" cmd...   (shows the command, its output, or that it is missing)
  local label="$1"; shift
  printf '**%s**\n' "$label"
  if have "$1"; then "$@" 2>&1 | head -40 | code; else printf '_not found: %s_\n' "$1"; fi
}
# Directories where the player stack usually lives; extend with SDHT_EXTRA_DIRS="/some/dir /other"
SEARCH_DIRS="$HOME/.local/share/omniphony $HOME/.local/lib $HOME/.local/bin $HOME/.config/mpv $HOME/.config/omniphony $HOME/.config/camilladsp \
$HOME/src $HOME/build $HOME/git $HOME/code $HOME/projects $HOME/Downloads $HOME/Applications /opt /usr/local /usr/lib /usr/share ${SDHT_EXTRA_DIRS:-}"
findf() { # findf name-pattern : files matching, depth-limited, only in SEARCH_DIRS
  for d in $SEARCH_DIRS; do [ -d "$d" ] && find "$d" -maxdepth 6 -iname "$1" -not -path '*/proc/*' 2>/dev/null; done | sort -u | head -20
}
gitinfo() { # gitinfo path : git commit, tag and remote of the repository holding path (if any)
  local d; d="$(dirname "$1")"
  while [ "$d" != "/" ] && [ ! -d "$d/.git" ]; do d="$(dirname "$d")"; done
  [ -d "$d/.git" ] || { echo "(not inside a git checkout)"; return; }
  echo "repo: $d"
  git -C "$d" describe --tags --always --dirty 2>&1
  git -C "$d" log -1 --format='commit %H%ndate   %cd%nsubject %s' 2>&1
  git -C "$d" remote -v 2>&1 | head -2
}
strings_ver() { # strings_ver file : the few version strings these Rust libraries embed (short, no binary noise)
  have strings || { echo "(strings not installed: sudo apt install binutils)"; return; }
  strings -n 5 "$1" 2>/dev/null | grep -a -o -E 'bridge_api;[0-9.]+|format_bridge[0-9.]+|abi_stable;[0-9.]+|rustc version [0-9.]+ \([^)]*\)|(harletty|orender|omniphony)[-_a-z]*[ -]v?[0-9]+\.[0-9]+\.[0-9]+' | sort -u | head -12
}
sums() { have sha256sum && sha256sum "$@" 2>/dev/null | cut -c1-16,65-; }   # first 16 hex digits of the hash, then the path

report() {
  printf '# SDHT versions and configuration\n\nCollected %s on %s by `scripts/collect-versions.sh` (read-only).\n' "$(date '+%F %T %Z')" "$(hostname)"

  h "System"
  { echo "kernel:  $(uname -srm)"
    [ -r /etc/os-release ] && . /etc/os-release && echo "os:      ${PRETTY_NAME:-?}"
    for f in sys_vendor product_name product_version; do [ -r /sys/class/dmi/id/$f ] && echo "$f: $(cat /sys/class/dmi/id/$f)"; done
    echo "cpu:     $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
    echo "memory:  $(awk '/MemTotal/ {printf "%.1f GB", $2/1048576}' /proc/meminfo)"
    echo "session: ${XDG_SESSION_TYPE:-?} / ${XDG_CURRENT_DESKTOP:-?}"; } | code
  have lspci && { printf '**GPU**\n'; lspci 2>/dev/null | grep -i -E 'vga|3d|display' | code; }
  have vainfo && { printf '**VAAPI**\n'; vainfo 2>&1 | grep -i -E 'vainfo|driver|VAProfile(HEVC|H264|AV1)' | head -10 | code; }

  h "PipeWire and WirePlumber"
  run "pipewire" pipewire --version
  run "wireplumber" wireplumber --version
  have pw-cli && { printf '**server (pw-cli info 0)**\n'; pw-cli info 0 2>/dev/null | grep -E 'version|name|clock|rate|quantum' | head -12 | code; }
  have pw-metadata && { printf '**clock settings**\n'; pw-metadata -n settings 2>/dev/null | head -12 | code; }
  have dpkg && { printf '**packages**\n'; dpkg -l 2>/dev/null | awk '/^ii/ && ($2 ~ /^(pipewire|wireplumber|libspa|alsa-ucm|libpipewire)/) {print $2, $3}' | head -20 | code; }

  h "CamillaDSP"
  run "binary" camilladsp --version
  for b in $(findf 'camilladsp' | grep -v '\.yml$' | head -3); do [ -x "$b" ] && [ -f "$b" ] && { printf '**%s**\n' "$b"; "$b" --version 2>&1 | head -2 | code; }; done
  if have systemctl; then
    printf '**user service**\n'; systemctl --user cat camilladsp.service 2>&1 | head -40 | code
    printf '**status**\n'; systemctl --user is-active camilladsp.service 2>&1 | code
  fi
  printf '**running process**\n'; (pgrep -a camilladsp || echo "(not running)") | code
  for c in $(findf '*.yml' | grep -i camilla | head -5); do printf '**config file: %s**\n' "$c"; head -250 "$c" | code; done
  have ss && { printf '**websocket / ports**\n'; ss -ltnp 2>/dev/null | grep -i camilla | code; }

  h "Omniphony (renderer, liborender)"
  mapfile -t LO < <(findf 'liborender*' ; findf 'libomniphony*')
  if [ ${#LO[@]} -eq 0 ]; then echo "_no liborender / libomniphony found in the searched directories ($SEARCH_DIRS). Re-run with SDHT_EXTRA_DIRS=\"/where/you/built/it\"._"; fi
  for f in "${LO[@]}"; do
    printf '**%s**\n' "$f"
    { ls -l "$f"; sums "$f"; strings_ver "$f"; gitinfo "$f"; } 2>&1 | code
  done
  for b in $(findf 'orender*' ; findf 'omniphony*' | grep -v -E '\.(so|conf|json|ya?ml|md|txt|lua|png)(\.|$)'); do
    [ -f "$b" ] && [ -x "$b" ] && { printf '**%s --version**\n' "$b"; timeout 5 "$b" --version 2>&1 | head -5 | code; }
  done
  have dpkg && { printf '**packages**\n'; dpkg -l 2>/dev/null | awk '/^ii/ && tolower($2) ~ /omniphony|orender/ {print $2, $3}' | code; }
  for d in $HOME/.config/omniphony $HOME/.local/share/omniphony; do
    [ -d "$d" ] && { printf '**contents of %s**\n' "$d"; find "$d" -maxdepth 3 -type f -printf '%TY-%Tm-%Td  %s  %p\n' 2>/dev/null | head -40 | code; }
  done

  for f in "$HOME/.config/omniphony/config.yaml" "$HOME/.config/omniphony/overlay-prefs.conf"; do
    [ -f "$f" ] && { printf '**%s**\n' "$f"; head -120 "$f" | code; }
  done

  h "harletty-bridge (Atmos decoder plugin)"
  mapfile -t HB < <(findf 'libharletty*' ; findf 'harletty*' | grep -v -E '\.(md|txt)$')
  if [ ${#HB[@]} -eq 0 ]; then echo "_no harletty files found in the searched directories. Re-run with SDHT_EXTRA_DIRS=\"/where/you/built/it\"._"; fi
  for f in "${HB[@]}"; do
    [ -f "$f" ] || [ -d "$f" ] || continue
    printf '**%s**\n' "$f"
    { ls -ld "$f"; [ -f "$f" ] && sums "$f"; [ -f "$f" ] && strings_ver "$f"; gitinfo "$f"; } 2>&1 | code
  done
  printf '**Is the plugin loaded by the running mpv?**\n'
  { for p in $(pgrep -x mpv; pgrep -f mpv-omniphony); do [ -r /proc/$p/maps ] && grep -h -i -E 'harletty|orender|omniphony' /proc/$p/maps | awk '{print $6}' | sort -u; done; } 2>/dev/null | sort -u | code
  have cargo && { printf '**cargo**\n'; cargo --version 2>&1 | code; cargo install --list 2>/dev/null | grep -i -E 'harletty|omniphony|orender' | code; }

  h "mpv (mpv-omniphony build)"
  for m in $( { which -a mpv-omniphony mpv 2>/dev/null; findf 'mpv-omniphony*' | grep -v -E '\.(md|txt|lua|conf)$'; command -v mpv-atmos >/dev/null && sed -n 's/^exec "\(.*\)" *\\$/\1/p' "$(command -v mpv-atmos)" | sed "s#\$HOME#$HOME#"; } | while read -r x; do readlink -f "$x" 2>/dev/null; done | sort -u ); do
    [ -f "$m" ] && [ -x "$m" ] && { printf '**%s**\n' "$m"; { ls -l "$m"; sums "$m"; timeout 8 "$m" --version 2>&1 | head -12; } | code; }
  done
  [ -f "$(command -v mpv-atmos 2>/dev/null)" ] && { printf '**wrapper: mpv-atmos (%s)**\n' "$(command -v mpv-atmos)"; cat "$(command -v mpv-atmos)" | head -80 | code; }
  W="$(command -v mpv-atmos 2>/dev/null || true)"
  for R in "$(dirname "$0")/mpv-atmos" "$(dirname "$0")/scripts/mpv-atmos"; do
    if [ -f "$R" ] && [ -n "$W" ] && [ "$(readlink -f "$R")" != "$(readlink -f "$W")" ]; then
      printf '**installed mpv-atmos against %s (diff; empty = identical)**\n' "$R"; diff "$W" "$R" 2>&1 | head -60 | code
    fi
  done
  have dpkg && { printf '**packages**\n'; dpkg -l 2>/dev/null | awk '/^ii/ && ($2 ~ /^(mpv|libmpv|ffmpeg|libavcodec|libplacebo|libvulkan|mesa-vulkan|intel-media|libva)/) {print $2, $3}' | head -20 | code; }

  h "mpv configuration (as used)"
  CFG="$(printf '%s\n' "$HOME/.config/mpv" "$HOME/.config/mpv-omniphony" "${XDG_CONFIG_HOME:-$HOME/.config}/mpv" | sort -u)"
  [ -f "$HOME/.config/mpv/mpv.conf" ] || echo "_There is no ~/.config/mpv/mpv.conf: mpv is configured by the command-line options in the mpv-atmos wrapper (above)._"
  for d in $CFG; do
    [ -d "$d" ] || continue
    printf '**%s**\n' "$d"; find "$d" -maxdepth 3 -type f -printf '%TY-%Tm-%Td  %s  %p\n' 2>/dev/null | sort | head -60 | code
    for f in mpv.conf input.conf; do
      [ -f "$d/$f" ] && { printf '**%s/%s**\n' "$d" "$f"; cat "$d/$f" | code; }
    done
    for f in "$d"/script-opts/*.conf "$d"/profiles/* ; do [ -f "$f" ] && { printf '**%s**\n' "$f"; head -25 "$f" | code; }; done
    ls "$d"/scripts 2>/dev/null | { printf '**scripts/**\n'; code; }
  done

  h "Audio devices (the 7.1 USB interface)"
  have aplay && { aplay -l 2>&1 | code; }
  have pactl && { pactl list short sinks 2>&1 | code; pactl info 2>&1 | grep -i -E 'server name|default sink|default source' | code; }

  h "Live links (only meaningful while a film plays)"
  if have pw-link; then
    printf '**mpv outputs**\n'; (pw-link -o 2>/dev/null | grep -i -E 'mpv|omniphony' || echo "(nothing from mpv: start a film and run again)") | code
    printf '**links into the camilladsp / router nodes**\n'; (pw-link -l 2>/dev/null | grep -i -B1 -A1 -E 'camilla|theater|sdht' | head -60 || true) | code
  fi
  have eq && { printf '**eq status**\n'; eq status 2>&1 | head -40 | code; }
  have theater-route && { printf '**theater-route**\n'; theater-route --help 2>&1 | head -10 | code; }
}

if [ "$REDACT" = 1 ]; then
  u="$(id -un)"; hn="$(hostname)"
  report 2>&1 | sed -e "s#$HOME#~#g" -e "s#/home/$u#/home/USER#g" -e "s#\b$u\b#USER#g" -e "s#\b$hn\b#HOST#g" \
    -E -e 's#(password|passwd|token|secret|key)[[:space:]]*=.*#\1=<REDACTED>#I' -e 's#(//)[^/@[:space:]]+:[^/@[:space:]]+@#\1USER:PASS@#g' > "$OUT"
else
  report > "$OUT" 2>&1
fi
cat "$OUT"
printf '\n---\nWritten to %s. Review it before you share it (mpv.conf can contain media paths or credentials).\n' "$OUT" >&2
