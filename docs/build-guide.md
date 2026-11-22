# Build guide

> **There is nothing to build yet.** This guide describes the build flow
> proposed in [architecture.md](architecture.md). Commands will be added once
> they exist and have been tested in Milestone M1. They are not shown here
> before then.

## Build environment (planned)

- **Host:** Debian 13 (trixie) amd64. This can be a privileged container in
  CI, a VM, or WSL2. live-build needs root for chroot and mounts.
- **Tools:** `live-build`, `debootstrap`, `squashfs-tools`, `xorriso`, `gpg`,
  `devscripts`, `debhelper`, `reprepro`. The exact list will live in
  `build/deps.list`.
- **Disk:** about 20 GB free for `cache/`, `work/` and `out/`.
- **Testing:** QEMU + OVMF (with the Secure Boot variables), and mkosi for
  disposable test VMs.

## Flow (planned)

1. **Resolve inputs.** Read `build/manifests/linbox-1.yaml`. It gives the
   Debian snapshot timestamp, the Linbox repo channel and version, and the
   package lists for each edition.
2. **Build packages.** Build every `packages/*` source package into
   `out/debs/` and index them in a local repo. In CI the packages come from
   the Linbox repo instead.
3. **Configure.** Copy `build/live-build/` to `work/lb/`, then run `lb config`
   with the mirrors set to
   `snapshot.debian.org/archive/debian/<timestamp>` and the Linbox repo
   added.
4. **Build.** Run `lb build` in `work/lb/`, with `SOURCE_DATE_EPOCH` set from
   the commit time.
5. **Emit metadata.** Write `out/SHA256SUMS`, `out/<iso>.build-info.json` and
   `out/<iso>.packages`.
6. **Smoke test.** Boot in QEMU/OVMF with Secure Boot, then check:
   - the live session reaches the Wayland desktop
   - a scripted Calamares install succeeds
   - after reboot, `linbox doctor --json` passes

All writes go to `cache/`, `work/` and `out/` at the repo root, which are
git-ignored. The build never modifies files under `build/`, `packages/` or
`desktop/`.
