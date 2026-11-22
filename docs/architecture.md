# Linbox OS — Technical Architecture

**Status:** Proposed (Phase 1). Nothing here is approved until the decisions in
[§10](#10-decisions-requiring-approval) are signed off. **Last verified against
upstream:** 2026-11-22.

## 1. Summary

Linbox OS is an Ubuntu 26.04 LTS derivative with an XFCE desktop on X11, aimed
at developers using refurbished business laptops.

The core architectural idea is this:

> **Everything that makes Linbox OS "Linbox" ships as Debian packages from a
> Linbox APT repository. The ISO is a thin, reproducible assembly step on top
> of an unmodified, checksum-pinned Ubuntu flavour image.**

This has several consequences:

- **One update path.** Installed systems receive branding, desktop defaults,
  the `linbox` CLI and fixes through `apt`, the same way they receive Ubuntu
  security updates. Nothing is applied only at ISO-build time and then
  forgotten.
- **The ISO tooling can be swapped.** If the image tool changes (see
  [image-build-options.md](image-build-options.md)), the packages don't.
- **Editions are just meta-packages.** The XFCE edition and a future Hyprland
  "Linbox Focus" edition share `linbox-base` and differ only in the
  top-level desktop meta-package and its settings package. There is no second
  OS to maintain.
- **Existing Ubuntu installs can be converted.** Adding the repository and
  installing `linbox-desktop` gives you most of Linbox OS. This is useful for
  testing and for the community.

## 2. Verified upstream facts (2026-11-22)

| Fact | Source |
|---|---|
| Ubuntu 26.04 LTS "Resolute Raccoon" released 2026-04-23; 26.04.1 is out. Standard support until April 2031. | [Ubuntu 26.04 release notes](https://documentation.ubuntu.com/release-notes/26.04/), [26.04.1 announcement](https://discourse.ubuntu.com/t/ubuntu-26-04-1-lts-released/86808/1) |
| Ubuntu Desktop (GNOME) 26.04 has **no Xorg session**; X11 apps run via Xwayland. | [26.04 LTS summary](https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/) |
| Xubuntu 26.04 ships Xfce 4.20, and Desktop and Minimal amd64 ISOs. The **flavour** is supported for 3 years (until April 2029). | [Xubuntu 26.04 release notes](https://xubuntu.org/releasedocs/26.04/release-notes/), [release page](https://xubuntu.org/release/26.04/) |
| Canonical's own docs (2026) name **livecd-rootfs** as the tool used to build both preinstalled and installer images. `PROJECT=xubuntu` with `SUBPROJECT=live` or `minimal` is a documented combination. | [Image cookbook: create installer image](https://ubuntu.com/hardware/docs/image-cookbook/howto/images/create_installer_image/) |
| For *customising* an installer ISO, Canonical's cookbook recommends **livefs-editor** over patching the build tools. | [Image cookbook: customise installer image](https://ubuntu.com/hardware/docs/image-cookbook/howto/images/customize_installer_image/) |
| The Ubuntu Desktop installer is a Flutter UI (`ubuntu-desktop-provision` / `ubuntu-desktop-bootstrap`) driving **subiquity**. It supports per-flavour white-labelling via `/usr/share/desktop-provision/whitelabel.yaml`, and `xubuntu` is a listed flavour. | [ubuntu-desktop-provision](https://github.com/canonical/ubuntu-desktop-provision) |
| The 26.04 desktop installer: TPM-backed FDE is GA; screen-reader support is incomplete; **OEM installs are not yet supported**. | [26.04 release notes](https://documentation.ubuntu.com/release-notes/26.04/) |
| A replacement for livecd-rootfs ("craft"-based) is in development but cannot yet build all image types. | Community reply by a Canonical engineer on [Discourse](https://discourse.ubuntu.com/t/how-to-create-my-own-bootable-image/77158). This is *not* official documentation. |

**Not yet verified, must be checked in Phase 2:**

- Whether Xubuntu 26.04 ships the Flutter installer or another one. It's
  strongly implied (its release notes link a subiquity bug), but its pages
  don't state it.
- Whether the default Xfce 4.20 session on Xubuntu 26.04 is X11. The pages
  don't state this either.
- What exactly the Minimal ISO omits compared with the Desktop ISO.

## 3. Base and desktop

| Layer | Choice | Notes |
|---|---|---|
| Base | Ubuntu 26.04 LTS, amd64, `resolute` | Unmodified Ubuntu kernel, shim, GRUB and signed boot chain. |
| Upstream image | **Xubuntu 26.04.x Minimal ISO**, pinned by SHA-256 | Starts small, which fits the "small clean base" goal. Xubuntu already integrates Xfce with the installer, LightDM and the archive seeds. |
| Desktop | Xfce 4.20 on X11 (LightDM) | Must verify the X11 default. Ubuntu GNOME's Xorg removal does not remove Xorg from the archive, but it signals reduced long-term investment ([R3](#9-risks)). |
| Display manager | LightDM + `lightdm-gtk-greeter`, Linbox-themed | Xubuntu default; it's themeable through config files. |
| Kernel | Ubuntu `linux-generic` (HWE as it becomes available) | No custom kernel. That keeps Secure Boot working with no MOK enrollment and gives us Canonical's security updates. |
| Snaps | Keep `snapd` (Xubuntu ships Firefox as a snap) | Decision **D6**. |

**Why Xubuntu as the upstream image rather than Ubuntu Desktop plus XFCE
added on:** Xubuntu's seeds, installer integration and LightDM setup already
exist and are tested by the flavour team on every release. Starting from
Ubuntu (GNOME) means removing GNOME and re-solving everything Xubuntu has
already solved.

## 4. Build and installer architecture

The full comparison is in [image-build-options.md](image-build-options.md).

**Recommendation:** remaster a pinned upstream Xubuntu Minimal ISO with
**livefs-editor**, driven by a declarative action file kept in this repo.
**livecd-rootfs** is the documented next step if remastering hits limits.

```
 source control (this repo)                      outside the repo
 ──────────────────────────                      ─────────────────────────────
 packages/*  ──(debuild/sbuild, CI)──▶ .debs ──▶ Linbox APT repo (signed)
                                                        │
 build/manifests/linbox-26.04.yaml                      │
   upstream ISO URL + sha256  ──download+verify──▶ cache/xubuntu-…-minimal.iso
   linbox packages to install ─┐                        │
 build/image/actions.yaml ─────┴──▶ livefs-edit ◀───────┘
                                        │
                                        ▼
                              out/linbox-os-26.04-<build-id>-amd64.iso
                              out/…SHA256SUMS, out/…build-info.json, manifest
```

In more detail:

- **Inputs** are only files in git, plus an upstream ISO verified against
  Canonical's signed `SHA256SUMS`, plus packages from the Linbox repository.
- **Outputs** go to `out/`, which git ignores. Nothing is written into source
  directories.
- **Build host:** a Ubuntu 26.04 Linux environment. The build needs root
  for loop mounts and squashfs, so a CI runner, VM or container with
  privileges. The developer workstation is Windows, so local builds run in a
  VM or WSL2. This must be validated ([R7](#9-risks)).
- **Installer:** the stock Xubuntu installer (subiquity with the Flutter UI),
  white-labelled through `whitelabel.yaml`, slides and accent colours shipped
  in a `linbox-installer-config` package. We don't fork the installer.
- **Factory installs (Linbox laptops):** use **autoinstall** with a
  Linbox-maintained `autoinstall.yaml`. The 26.04 desktop installer does not
  support OEM mode, so factory flows must be validated rather than assumed
  ([R4](#9-risks)).

## 5. Package architecture

All packages are Debian-native, built with `debhelper`, and live under
`packages/`.

| Package | Kind | Contents |
|---|---|---|
| `linbox-keyring` | data | Linbox archive signing key(s) in `/usr/share/keyrings/`. |
| `linbox-repository` | config | deb822 `/etc/apt/sources.list.d/linbox.sources` with `Signed-By`, channel selection. |
| `linbox-base` | meta + config | Depends: keyring, repository, `linbox-system`; OS identity (D5); small sane system defaults. Editions share this. |
| `linbox-system` | app | The `linbox` CLI (version, doctor, hardware, update, recovery, support) and the config-migration framework. |
| `linbox-branding` | data | Wallpapers, GTK/xfwm4 theme, icon theme selection, fonts, Plymouth theme, LightDM greeter theme. |
| `linbox-desktop-settings` | config | Xfce system-wide defaults in `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/`, panel layout, terminal profile, keyboard shortcuts, workspaces. |
| `linbox-desktop` | meta | XFCE edition: Depends `linbox-base`, `linbox-branding`, `linbox-desktop-settings`, selected Xfce/Ubuntu packages. |
| `linbox-installer-config` | config | Installer white-label, slides, autoinstall defaults. Live session only. |
| `linbox-developer` | app | Developer Setup GUI plus profile definitions (Phase 3). |
| `linbox-hardware` | data + config | Per-model quirks keyed on DMI, the hardware DB snapshot for `linbox hardware` (Phase 4). |
| *(future)* `linbox-desktop-focus` | meta | Hyprland edition. It reuses `linbox-base` and `linbox-branding` assets. |

### Configuration management rules

1. **System defaults, not home directories.** Xfce reads
   `$XDG_CONFIG_DIRS/xfce4/xfconf/...`, so Linbox defaults go in `/etc/xdg`.
   User customisations in `~/.config` always take precedence and are never
   touched by package upgrades.
2. **Migrations are explicit and versioned.** When a default must change for
   existing users (for example a renamed panel plugin), `linbox-system` ships
   a numbered migration. It runs per user at login, is idempotent, records its
   state in `~/.local/state/linbox/migrations`, backs up any file it changes,
   and never deletes user data.
3. **conffile hygiene.** Files under `/etc` are dpkg conffiles. Local admin
   edits trigger the standard dpkg prompt and are never silently overwritten.
   Where we must alter a file owned by another package, we use
   `dpkg-divert`, documented in `docs/system-modifications.md` (Phase 2).
4. **No fragile scripts.** No "run this to theme your desktop" scripts. If a
   setting cannot be expressed as a packaged default, it goes through rule 2.

## 6. Repository and channel strategy

- **Channels** are APT suites: `resolute` (stable) and `resolute-testing`.
  Packages are built once, land in testing, and are **promoted** (copied) to
  stable unchanged after validation. There are no rebuilds between channels.
- **Hosting (D3):** start with **Launchpad PPAs**, `ppa:linbox/testing` and
  `ppa:linbox/stable`, which Launchpad builds from signed source uploads.
  That gives free, trusted build infrastructure, signing and mirroring, and
  promotion is "copy package between PPAs". Move to a self-hosted
  `reprepro`/`aptly` repository on `apt.linbox.in` once we need things PPAs
  can't do (custom suite names, staged rollouts, private hardware packages).
  Package sources don't change either way.
- **Third-party repositories** are never enabled in the base image. Developer
  Setup may add vendor repositories (Docker, VS Code, …) **only** when the
  user picks that profile, with the vendor's signing key pinned by
  fingerprint and a matching uninstall path.

## 7. Versioning

| Thing | Scheme | Example |
|---|---|---|
| OS release | Tracks the Ubuntu base | `Linbox OS 26.04`, point releases `26.04.1` |
| Pre-releases | `-devN`, `-previewN`, `-rcN` | `26.04-preview1` |
| Image build ID | `YYYYMMDD.N` | `linbox-os-26.04-preview1-20261205.1-amd64.iso` |
| Linbox packages | SemVer-ish Debian native | `linbox-system 0.3.0` |
| Config migrations | Monotonic integers per package | `linbox-desktop-settings/0004-…` |

Every ISO ships `/usr/share/linbox/build-info.json` with:

- the build ID
- the git commit
- the upstream ISO name and SHA-256
- the Linbox package versions
- the builder environment

Next to the ISO it ships `SHA256SUMS` and a full package manifest
(`dpkg-query` output).

## 8. Developer experience, CLI and updates (Phase 3 outline)

- **`linbox` CLI:** Python 3 using the standard library only (Python is
  always present on Ubuntu). It has structured output (`--json`) for support
  engineers. Every command either works or exits non-zero with a clear "not
  implemented yet"; none reports false success.
- **Developer Setup:** a GTK application (toolkit decision deferred to Phase
  3) that runs **declarative profiles**. Each step says what it installs,
  where from, and how to undo it. Privileged steps go through `pkexec` with a
  narrow polkit policy, and user-space toolchains (fnm, uv, SDKMAN, Flutter)
  install as the user with no root. Downloads are verified against checksums
  or signatures. There is no `curl | sudo bash`.
- **Updates:** `linbox update` wraps apt with pre-flight checks (disk space,
  repo health, held/broken packages, power state) and a post-update
  migration run. Unattended security updates stay Ubuntu's standard
  `unattended-upgrades` default. There is no automatic destructive cleanup.
- **Recovery (D7):** see [§11](#11-recovery-and-snapshots).

## 9. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R1 | **Xfce lives in Ubuntu *universe*.** Universe security fixes are community best-effort under standard support; Canonical's universe coverage is via Ubuntu Pro (ESM-Apps). The Xubuntu flavour's own support ends April 2029. | Decision **D8**: Linbox takes ownership of tracking Xfce security fixes and/or evaluates Ubuntu Pro for shipped laptops (check licensing for commercial resale). Plan the 28.04 rebase before April 2029. |
| R2 | **Ubuntu trademark and Canonical IP policy.** Redistributing a modified Ubuntu-based image under a new name requires removing or replacing Ubuntu/Xubuntu trademarks and artwork where policy requires. | Decision **D9**: review Canonical's [IP rights policy](https://ubuntu.com/legal/intellectual-property-policy) before the first *public* ISO. Replace logos and branding; describe the product as "based on Ubuntu". |
| R3 | **X11 longevity.** Ubuntu's flagship desktop has dropped Xorg. | Fine for the 26.04 cycle. Linbox Focus (Hyprland/Wayland) and Xfce's Wayland work are the long-term path. Re-evaluate at 28.04. |
| R4 | **Installer gaps** (no OEM mode, incomplete screen reader, known Xubuntu installer bugs such as a double root partition). | Validate install and autoinstall in VMs every build. Factory provisioning via autoinstall, not OEM mode. Accessibility is called out in release notes. |
| R5 | **livefs-editor's fit with the layered Desktop installer ISO is unproven.** The cookbook example is Server/riscv64. | Phase 2 spike. If it can't place packages into the layer the installer copies, switch to livecd-rootfs `PROJECT=xubuntu` (packages are unaffected). |
| R6 | **Intel IPU6 / OV02C10 webcams** may not work out of the box. | Hardware DB marks them `untested` until proven. No support claim without a tested report. |
| R7 | **Build environment.** The primary workstation is Windows. | Build in CI (Ubuntu container with privileges) plus a local Linux VM or WSL2. To be validated in Phase 2. |
| R8 | **Telemetry defaults.** The Ubuntu installer and desktop may offer system-data reporting. | Audit in Phase 2. Linbox default is off and opt-in only. |
| R9 | **Changing `/etc/os-release` `ID`** breaks third-party installers that check `ID=ubuntu`. | Decision **D5**. |

## 10. Decisions requiring approval

| ID | Decision | Recommendation | Alternatives |
|---|---|---|---|
| **D1** | Upstream base image | **Xubuntu 26.04.x Minimal amd64**, SHA-pinned | Xubuntu Desktop (bigger); Ubuntu Desktop + XFCE (remove GNOME, more work) |
| **D2** | Primary ISO build tool | **livefs-editor remaster**, with livecd-rootfs as the fallback | livecd-rootfs from day one; Cubic (GUI, not reproducible); live-build or debootstrap from scratch plus Calamares (own installer to maintain) |
| **D3** | Package hosting | **Launchpad PPAs** (testing → stable copy) now; self-host later | Self-hosted reprepro/aptly now; GitHub Releases (not a real APT repo) |
| **D4** | Channel model | `resolute` and `resolute-testing`, promote without rebuild | Single channel plus tags |
| **D5** | OS identity | `/etc/os-release`: `NAME="Linbox OS"`, `ID=linbox`, `ID_LIKE="ubuntu debian"`, keep `UBUNTU_CODENAME=resolute` and `VERSION_CODENAME`. Pop!_OS uses this pattern. | Keep `ID=ubuntu` and only change `NAME`/`PRETTY_NAME` (max compatibility, weaker identity) |
| **D6** | Snaps | Keep snapd (needed by stock Firefox), no extra snaps in base | Remove snapd and use Mozilla's APT repo for Firefox (adds a third-party repo) |
| **D7** | Default filesystem and recovery | ext4 + documented recovery + `linbox recovery` tooling now. Evaluate Btrfs + Snapper as an *opt-in* in Phase 5 (see §11). | Btrfs + Snapper default now |
| **D8** | Xfce security ownership | Linbox monitors Xfce/universe CVEs and evaluates Ubuntu Pro for shipped laptops | Rely on community universe maintenance |
| **D9** | Trademark review before first public ISO | Yes: blocking for the public developer preview | — |
| **D10** | CLI implementation language | Python 3, stdlib only | Bash (hard to test and structure); Go/Rust (extra toolchain, larger binaries) |

## 11. Recovery and snapshots

| Option | Pros | Cons |
|---|---|---|
| **ext4 + apt discipline + recovery docs** | Simplest and most tested; installer default; no surprises on refurbished SSDs | No rollback; recovery means fixing forward or reinstalling `/` while keeping `/home` |
| ext4 + Timeshift (rsync) | Works on ext4; user-friendly | Slow, uses lots of space, is not atomic, and restoring a running system is fragile |
| Btrfs + Snapper (+ grub-btrfs) | Cheap atomic pre/post-update snapshots; boot into a snapshot | Must check whether the 26.04 desktop installer's guided partitioning supports a sane Btrfs subvolume layout; more support complexity; `/boot` handling |
| LVM thin snapshots | Filesystem-agnostic | Complex for users; the installer's LVM is tied to its FDE layout |
| A/B or image-based (transactional) | Strongest guarantees | Fights APT's model; very high engineering cost; wrong for Milestone 1 |

**Recommendation:** ext4 for 26.04. To keep future options open:

- `linbox update` already uses pre- and post-hooks, so a snapshot backend can
  be plugged in later.
- The installer layout keeps `/home` easy to preserve.
- Btrfs + Snapper gets a dedicated evaluation in Phase 5 as an *opt-in*
  install option before any default change.

## 12. Initial repository structure

```
linbox-os/
├── README.md  LICENSE  CONTRIBUTING.md
├── docs/                    architecture, build options, build guide, hardware, release, security, roadmap
├── build/
│   ├── manifests/           image manifests (upstream ISO pin, packages per edition)
│   ├── image/               livefs-editor action files, overlay files for the live session
│   ├── installer/           autoinstall + installer white-label sources
│   └── scripts/             build entry points (Phase 2)
├── packages/                one directory per Debian source package (Phase 2+)
├── desktop/                 design sources (theme, wallpapers SVG, shortcuts) consumed by packages
├── hardware/
│   ├── compatibility/       hardware DB (one YAML per model) + schema
│   └── diagnostics/         collectors used by `linbox hardware` (Phase 4)
├── tests/                   image/VM smoke tests, package tests
└── tools/                   developer utilities (lint, validation)
```

These directories don't exist yet and arrive in the phase that first needs
them: `applications/` (Developer Setup, Phase 3) and `repository/`
(self-hosted repo config, if D3 changes). Build artefacts always go to
`out/`, `work/` or `cache/`, which are git-ignored.
