# Milestone plan

Each milestone ends in a **buildable, tested state**. Exit criteria are
checked by a person and recorded in the PR that closes the milestone. Decision
IDs (D1…) and risk IDs (R1…) refer to [architecture.md](architecture.md).

## M0 — Architecture and foundation (Phase 1) — done

- Architecture proposal, image-build comparison, hardware strategy, release
  and security policy, repo skeleton, image manifest pinned to a Debian
  snapshot.
- **Exit:** D4–D13 approved or amended. D1 (Debian 13), D2 (Wayland only)
  and D3 (KDE Plasma 6) are already decided.

## M1 — Build spike (Phase 2a) — done, except the manual Calamares install check

- Linux build environment: a privileged Debian 13 container in CI, plus a
  local VM or WSL2 (R6).
- A minimal live-build config pinned to `snapshot.debian.org`. It contains
  Plasma 6 on Wayland (D3), Calamares, and **one trivial test package** from
  a local repo.
- Verify the open items:
  - Calamares in a Wayland-only live session
  - the display manager's Wayland greeter
  - Secure Boot with Debian's signed chain
- **Exit:** the M1 criteria in [image-build-options.md](image-build-options.md):
  - it boots with UEFI + Secure Boot in QEMU/OVMF
  - the Calamares install succeeds
  - the installed system contains the test package
  - two builds produce identical package manifests

## M2 — First bootable Linbox ISO (Phase 2b) — in progress

- Packages: `linbox-keyring`, `linbox-repository`, `linbox-base`,
  `linbox-branding` (first pass), `linbox-desktop-settings` (first pass),
  `linbox-desktop`, `linbox-installer-config`.
- `linbox-system` with `linbox version` and a read-only `linbox doctor`
  (repo health, disk, memory, failed units, network).
- A Linbox APT repo (D5) with the `trixie-testing` channel: reprepro in CI,
  GitHub Pages at `apt.linbox.in` ([apt-repository.md](apt-repository.md)).
- The ISO ships with build-info, SHA256SUMS and a package manifest.
- **Exit:** installs in a VM (UEFI and Secure Boot), boots to a branded
  Wayland session with no Xorg installed, `apt update && apt full-upgrade` is
  clean, and `linbox doctor` output is accurate.

## M3 — Developer experience (Phase 3)

- Developer Setup app and the four profiles, with progress, failure reporting,
  retry and uninstall notes.
- Wayland and Xwayland compatibility testing of the profile tools (R2):
  Android Studio + emulator, JetBrains IDEs, VS Code, Flutter.
- `linbox update` (pre-flight checks plus migrations), `linbox recovery` docs
  and helpers, a fuller `linbox doctor`.
- **Exit:** each profile installs and uninstalls cleanly in a fresh VM, and a
  failure-injection test shows errors and lets the user retry.

## M4 — Hardware validation (Phase 4)

- Test the ZeroBook, write the first hardware report, `linbox hardware`,
  `linbox-hardware` quirks, and the kernel/backports policy in practice (D10).
- Pick the first ThinkPad, Latitude and EliteBook generations and test them.
- Factory provisioning decision (D11).
- **Exit:** at least one model with every component in a non-`untested`
  state, and a published list of known limitations.

## M5 — Release engineering and Developer Preview (Phase 5)

- Testing → stable promotion, automated nightly ISO builds, VM install and
  upgrade tests in CI.
- Btrfs + Snapper opt-in evaluation (D9). Trademark review done (D12).
- **Exit:** public **Linbox OS 1.0 Developer Preview 1**, with release notes,
  checksums and signed artefacts.
