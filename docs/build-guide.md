# Build guide

> **There is nothing to build yet.** This guide describes the build flow
> proposed in [architecture.md](architecture.md). Commands will be added once
> they exist and have been tested in Milestone M1. They are not shown here
> before then.

## Build environment (planned)

- **Host:** Ubuntu 26.04 (`resolute`) amd64. This can be a VM, a privileged
  container in CI, or WSL2. The build needs root for loop mounts and squashfs.
- **Tools:** `livefs-editor` (pinned git revision), `squashfs-tools`,
  `xorriso`, `gpg`, `devscripts`, `debhelper`, `sbuild` or `dpkg-buildpackage`.
  The exact list will live in `build/requirements.txt` or `build/deps.list`.
- **Disk:** about 20 GB free for `cache/`, `work/` and `out/`.
- **Testing:** QEMU + OVMF (with the Secure Boot variables) for UEFI and
  Secure Boot boot tests.

## Flow (planned)

1. **Fetch upstream.** Read `build/manifests/linbox-26.04.yaml`, download the
   pinned Xubuntu ISO into `cache/`, verify `SHA256SUMS.gpg` against Ubuntu's
   CD image signing key, then verify the ISO's SHA-256. The build aborts on
   any mismatch.
2. **Build packages.** Build every `packages/*` source package into
   `out/debs/`. In CI the packages come from the Linbox repo (PPA) instead.
3. **Remaster.** Run `livefs-edit cache/<upstream>.iso out/<linbox>.iso
   --action-yaml build/image/actions.yaml`.
4. **Emit metadata.** Write `out/SHA256SUMS`, `out/<iso>.build-info.json` and
   `out/<iso>.manifest`.
5. **Smoke test.** Boot in QEMU/OVMF, run an unattended install through
   autoinstall, reboot, and run `linbox doctor --json`.

All writes go to `cache/`, `work/` and `out/` at the repo root, which are
git-ignored. The build never modifies files under `build/`, `packages/` or
`desktop/`.
