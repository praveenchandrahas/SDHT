# Repository split (2026-10-25)

The project began as one repository holding several independent sub-projects. It was divided so that each can be used, versioned and shared on its own. Each new repository
was cut from this one with `git filter-repo`, so **every file keeps its history** (commit hashes differ).

## The repositories and what depends on what

| Repository | Contents (original paths) | Needs |
|---|---|---|
| `sdht` | `docs/`, `README.md`, `CHANGELOG.md`, `scripts/preflight`, `scripts/collect-versions.sh`, the `tools/make-*.py` figure scripts, `docs/graphs`, `docs/img` | reads the others (figures, preflight) |
| `theater-router` | `scripts/theater-route`, `set-eq.py`, `install-autoroute.sh`, `route-mpv.sh`, `make-default.sh`, `configs/`, router and config tests | **`upmix-engine`** (`set-eq.py` imports `upmix`; the installer copies `upmix.py` and `upmix_engine.py`) |
| `upmix-engine` | `scripts/upmix.py`, `scripts/upmix_engine.py`, `tools/upmixtest/`, `tests/test_engine.py` | nothing to run; its test harness (`upmixtest/harness.py`) reads `set-eq.py` from `theater-router` |
| `mpv-object-audio` | `scripts/object-audio-install.sh`, `mpv-object-audio`, `mpv-atmos`, `mpv-atmos-overlay-off.lua`, `docs/omniphony-debugging.md` | nothing; optionally calls `eq` from `theater-router` |
| `seekthumbs` | `tools/seekthumbs/` (now the repo root), `docs/seekthumbs.md` (now the README), its test | nothing; works with any mpv + uosc |
| `theater-measurement` | `tools/{sweeptest,subtest,reflecttest,dialoguetest,bartest}`, `tools/analyze-delaytest.py`, `scripts/{rec.sh,tone-test.sh,make-bedtest.py,make-delaytest.py}`, `data/`, `docs/measurement.md` | nothing (the kits use each other inside the repo) |
| `drift-tracker` | `tools/drifttest/` (now the repo root), `tests/test_drift.py` | nothing |

There are two real couplings: **router to upmix-engine** (a runtime import) and **figure scripts and `preflight` to the others** (they read files from sibling repositories).

## How the repositories find each other

Clone them side by side (`scripts/clone-all.sh`), keeping the folder names. Lookups use the sibling folder, with an environment variable to override:
`SDHT_WORKSPACE` (the parent folder; figure scripts, `preflight`, `test-all.sh`), `UPMIX_ENGINE_DIR` (router and its tests and installer), `THEATER_ROUTER_DIR` (the upmix test harness).
Installed copies in `~/.local/bin` are unchanged: the router, `set-eq.py`, `upmix.py` and `upmix_engine.py` still sit side by side there.

## Checking the whole thing

`scripts/test-all.sh` runs the tests of every sibling that has some (router and config, engine, drift tracker, player syntax, seekthumbs): 159 router, engine and drift checks as before the split, plus the seekthumbs suite.
`scripts/preflight` compares the installed scripts with the right repository.

## Known loose ends

- Prose in the documentation names files by their old path (`scripts/set-eq.py`, `tools/sweeptest/`); links were rewritten to the new repositories, plain mentions were not. The table above maps old paths to repositories.
- Code comments in the new repositories still point at `docs/runbook.md` and similar; those documents are in `sdht`.
- The sandbox that prepared the split cannot create GitHub repositories. The new repositories are published with `publish-split.sh` (in the bundle that came with this change).
