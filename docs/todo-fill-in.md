# Things only the owner can fill in

Search the docs for `TODO(owner)`. Checklist:

- [ ] Laptop model, OS and kernel version; PipeWire and WirePlumber versions (`pipewire --version`)
- [ ] `systemctl --user cat camilladsp.service` (replace `configs/systemd/camilladsp.service.example`)
- [ ] The exact `mpv-atmos` command or alias, and `mpv.conf` (video side included)
- [ ] Omniphony install and configuration steps, with upstream links and versions (liborender 0.3.0, ABI 0.6, commit 6ffaf21)
- [ ] harletty-bridge version and how it is wired to mpv
- [ ] `pw-link -o | grep mpv` while Atmos plays and while a 5.1 file plays (see [status.md](status.md))
- [ ] Z906 sub-level and master-volume reference positions (photo in `docs/img/`)
- [ ] Exact room dimensions (notes from 2026-10-19 said about 10 x 11 ft; later 10 x 10 ft) and a floor plan with seat and speaker positions
- [ ] Paths of the Omniphony and mpv configuration for the backup list in [runbook.md](runbook.md#backups)
- [ ] Choose a licence and add a `LICENSE` file
- [ ] Decide what to keep out of a public repository (library mount details, personal details)
