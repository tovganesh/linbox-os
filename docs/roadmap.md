# Milestone plan

Each milestone ends in a **buildable, tested state**. Exit criteria are
checked by a person and recorded in the PR that closes the milestone. Decision
IDs (D1…) and risk IDs (R1…) refer to [architecture.md](architecture.md).

## M0 — Architecture and foundation (Phase 1) ← *this PR*

- Architecture proposal, image-build comparison, hardware strategy, release
  and security policy, repo skeleton, image manifest with a pinned upstream
  ISO.
- **Exit:** D1–D10 approved or amended.

## M1 — Build spike (Phase 2a)

- Linux build environment: CI job plus a local VM or WSL2 (R7).
- `build/scripts/fetch-upstream`: download the pinned ISO, verify the GPG
  signature on `SHA256SUMS`, then verify the SHA-256.
- Remaster with livefs-editor, adding **one trivial test package** from a
  local repo.
- **Exit:** the R5 criteria in
  [image-build-options.md](image-build-options.md). That means the ISO boots
  with UEFI + Secure Boot in QEMU/OVMF, and the installed system contains the
  test package. If it fails, switch to livecd-rootfs (ADR update).

## M2 — First bootable Linbox ISO (Phase 2b)

- Packages: `linbox-keyring`, `linbox-repository`, `linbox-base`,
  `linbox-branding` (first pass), `linbox-desktop-settings` (first pass),
  `linbox-desktop`, `linbox-installer-config`.
- `linbox-system` with `linbox version` and a read-only `linbox doctor`
  (repo health, disk, memory, failed units, network).
- PPA (D3) or a local repo for testing. ISO with build-info, SHA256SUMS and a
  package manifest.
- Telemetry audit (R8), trademark scrub plan (R2).
- **Exit:** installs in a VM (UEFI and Secure Boot), boots to a branded Xfce
  session, `apt update && apt full-upgrade` is clean, and `linbox doctor`
  output is accurate.

## M3 — Developer experience (Phase 3)

- Developer Setup app and the four profiles, with progress, failure reporting,
  retry and uninstall notes.
- `linbox update` (pre-flight checks plus migrations), `linbox recovery` docs
  and helpers, a fuller `linbox doctor` (battery, firmware, pending updates).
- **Exit:** each profile installs and uninstalls cleanly in a fresh VM, and a
  failure-injection test shows errors and lets the user retry.

## M4 — Hardware validation (Phase 4)

- Test the ZeroBook, write the first hardware report, `linbox hardware`,
  `linbox-hardware` quirks.
- Pick the first ThinkPad, Latitude and EliteBook generations and test them.
- **Exit:** at least one model with every component in a non-`untested`
  state, and a published list of known limitations.

## M5 — Release engineering and Developer Preview (Phase 5)

- Testing → stable promotion, automated nightly ISO builds, VM install and
  upgrade tests in CI.
- Upgrade test: install the previous preview, upgrade to the new one, then run
  migrations.
- Btrfs/Snapper opt-in evaluation (D7), trademark review done (D9).
- **Exit:** public **Linbox OS 26.04 Developer Preview 1**, with release notes,
  checksums and signed artefacts.
