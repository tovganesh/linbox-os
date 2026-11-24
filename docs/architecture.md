# Linbox OS — Technical Architecture

**Status:** Approved (Phase 1). All decisions in [§10](#10-decisions) were
signed off by the maintainer on 2026-11-22. D11 is approved as a deferral to
M4. Changes to approved decisions go through a PR that updates §10.
**Last verified against upstream:**
2026-11-22.

**Revision 2:** changed the base from Ubuntu 26.04 / Xubuntu to **Debian 13
"trixie"**, and the display stack to **Wayland only (no Xorg)**, as directed
by the maintainer. Both changes ripple through the build, installer,
packaging and desktop choices below.

## 1. Summary

Linbox OS is a Debian 13 "trixie" derivative with a Wayland-only desktop,
aimed at developers using refurbished business laptops.

The core architectural idea is this:

> **Everything that makes Linbox OS "Linbox" ships as Debian packages from a
> Linbox APT repository. The ISO is a reproducible live-build assembly of
> Debian's archive plus those packages, pinned to a point in time.**

This has several consequences:

- **One update path.** Installed systems receive branding, desktop defaults,
  the `linbox` CLI and fixes through `apt`, alongside Debian's security
  updates. Nothing is applied only at ISO-build time and then forgotten.
- **Editions are just meta-packages.** The default edition and a future
  Hyprland "Linbox Focus" edition share `linbox-base` and differ only in a
  desktop meta-package plus its settings package. There is no second OS to
  maintain.
- **Existing Debian installs can be converted.** Adding the repository and
  installing `linbox-desktop` gives you most of Linbox OS.

## 2. Verified upstream facts (2026-11-22)

| Fact | Source |
|---|---|
| Debian 13 "trixie" was released 2025-08-09. The latest point release is **13.7** (2026-09-12). It is supported for 5 years through the Debian Security team plus Debian LTS. | [Trixie announcement](https://www.debian.org/News/2025/20250809), [stable errata](https://www.debian.org/releases/stable/errata.en.html) |
| Trixie ships Linux **6.12 LTS**, **GNOME 48**, **KDE Plasma 6.3** (the first Debian release with Plasma 6), **Xfce 4.20** and **LXQt 2.1**. | [What's new in Debian 13](https://www.debian.org/releases/stable/release-notes/whats-new.html) |
| Official Debian live ISOs are built with **live-build** and ship the **Calamares** installer. The configs live in the live team's `live-setup` repository. | [Debian Live](https://www.debian.org/devel/debian-live/), [live install images](https://www.debian.org/CD/live/), [live team on Salsa](https://salsa.debian.org/live-team) |
| Debian's reproducible-builds work rebuilds the official trixie live images with live-build. The core squashfs reproduces; the 13.2 ISOs as a whole did not. | [Reproducible live images](https://wiki.debian.org/ReproducibleInstalls/LiveImages) |
| **Xfce's Wayland session is experimental.** xfwm4 stays X11-only; on Wayland, xfce4-session runs inside **labwc** (or Wayfire), so xfwm4 themes and shortcuts don't apply. A new compositor, **xfwl4**, is in development, with no stable release found. | [Xfce Wayland roadmap](https://wiki.xfce.org/releng/wayland_roadmap), [ArchWiki: Xfce](https://wiki.archlinux.org/title/Xfce), [GamingOnLinux on xfwl4](https://www.gamingonlinux.com/2026/01/xfce-is-getting-a-brand-new-wayland-compositor-called-xfwl4/) |
| labwc is in production use as the default desktop compositor of Raspberry Pi OS (Wayland on all models since Nov 2024, with Xwayland for X11 apps). | [Raspberry Pi announcement](https://raspberrypi.com/news/a-new-release-of-raspberry-pi-os) |

**Not yet verified, must be checked in Milestone M1:**

- Calamares running in a Wayland-only live session.
- The SDDM Wayland greeter on trixie.
- Whether trixie-backports kernels are Secure Boot-signed.
- Hyprland's packaging status in Debian (for the future Focus edition).

## 3. Base and display stack

| Layer | Choice | Notes |
|---|---|---|
| Base | Debian 13 "trixie" stable, amd64 | Components `main` + **`non-free-firmware`**. Intel Wi-Fi, i915 GuC/HuC and SOF audio need it, and Debian's own installer images include it by default. No `contrib`/`non-free` in the base. |
| Kernel | Debian `linux-image-amd64` (6.12 LTS) | Debian-signed shim, GRUB and kernel, so Secure Boot works. A newer kernel from `trixie-backports` only for a model with a *tested* need (D10). |
| Display | **Wayland only.** No Xorg server, no X11 session. | Xwayland stays installed so X11-only apps (some Java/JetBrains/Android tooling, older Electron) still run inside the Wayland session (D2). |
| Desktop | **KDE Plasma 6 (6.3 in trixie) on Wayland** (D3) | SDDM login with a Wayland greeter (to verify in M1), KWin, a Linbox Global Theme. See [§3.1](#31-desktop-environment-under-wayland-only). |
| Apps | Debian packages. **No snaps.** | Firefox ESR from Debian by default. Flatpak/Flathub offered opt-in through Developer Setup (D8). |

### 3.1 Desktop environment under "Wayland only"

The original brief asked for XFCE, and Wayland-only rules out XFCE's mature
(X11) session. These are the realistic options on trixie:

| Option | Maturity on Wayland | Weight | Identity / theming | Accessibility | Linbox maintenance |
|---|---|---|---|---|---|
| **A. KDE Plasma 6.3** *(recommended)* | Mature; Wayland is Plasma 6's default session | Medium | Strong: a **Global Theme ("Look and Feel") package** sets colours, panels, layout, shortcuts and splash in one versioned bundle | Good (Orca, magnifier, high contrast) | **Low**: we ship packaged defaults, not glue code |
| B. Xfce 4.20 components on labwc | Upstream calls it **experimental**. No xfwm4 shortcuts/themes; screen lock and display config need non-Xfce pieces | Light | Medium: Xfce theming plus separate labwc theming | Fair | **High**: Linbox becomes the integrator of an unfinished session, and must migrate again when xfwl4 lands |
| C. GNOME 48 | Most mature | Medium–heavy | Weak: upstream discourages theming, and extensions break between releases | Best | Low, but hard to make distinctive |
| D. Custom labwc/Sway + panel (waybar etc.) | Compositor mature; the whole desktop is ours | Light | Total | Poor unless we build it | **Very high**: the "collection of fragile scripts" the brief warns against |

**Recommendation: A, KDE Plasma 6 on Wayland.** It is the only option that is
lightweight enough for 8 GB+ business laptops, mature on Wayland, and designed
for a distribution to rebrand through one packaged Global Theme. It also fits
the "central configuration package" requirement directly. Keyboard-centric
users get KWin tiling and shortcuts now, and the Hyprland Focus edition later.

**Decision (2026-11-22): Plasma 6 on Wayland.** Xfce can come back as an
experimental edition once xfwl4 ships stable. Because editions are just
meta-packages, adding one later doesn't affect the base.

Desktop-specific parts below are marked *(Plasma, per D3)*.

## 4. Build and installer architecture

The full comparison is in [image-build-options.md](image-build-options.md).

**Recommendation:** **live-build**, Debian's own tool and the one used for
official Debian live ISOs, producing a live ISO with the **Calamares**
installer, configured by a `linbox-installer-config` package.

```
 source control (this repo)                       outside the repo
 ──────────────────────────                       ─────────────────────────────
 packages/*  ──(dpkg-buildpackage in CI)──▶ .debs ──▶ Linbox APT repo (signed)
                                                            │
 build/manifests/linbox-1.yaml                              │
   Debian snapshot timestamp ──▶ snapshot.debian.org ───────┤
   edition package lists                                    │
 build/live-build/ (lb config tree) ──▶ lb build ◀──────────┘
                                          │
                                          ▼
                       out/linbox-os-1.0-<build-id>-amd64.iso
                       out/…SHA256SUMS, out/…build-info.json, out/…packages
```

- **Reproducibility:** the build points apt at
  **`snapshot.debian.org/archive/debian/<timestamp>`**, a frozen view of the
  Debian archive, plus a pinned Linbox repo version. Rebuilding the same commit
  then resolves the same package versions. `SOURCE_DATE_EPOCH` is set from the
  commit.
- **Outputs:** `out/`, `work/` and `cache/`, all git-ignored. live-build's
  working tree is copied out of `build/` before building, so nothing writes
  into source directories.
- **Build host:** Debian 13 with root (live-build needs chroot and mounts):
  a CI container with privileges, or a local Linux VM or WSL2. The developer
  workstation is Windows, so this must be validated (R6).
- **Installer:** Calamares with Linbox branding, slideshow and partition
  defaults. Calamares supports LUKS full-disk encryption and **Btrfs with
  subvolumes**, which matters for D9. It does not do TPM-backed unlock.
- **Factory installs (Linbox laptops):** Calamares isn't built for unattended
  installs. Two candidates, to decide in M4 (D11):
  - **debian-installer with a preseed file:** official and fully automated.
  - **A preinstalled disk image built with mkosi or debos:** flashed, then
    grown on first boot.

## 5. Package architecture

All packages are Debian-native, built with `debhelper`, and live under
`packages/`.

| Package | Kind | Contents |
|---|---|---|
| `linbox-keyring` | data | Archive signing key(s) in `/usr/share/keyrings/`. |
| `linbox-repository` | config | deb822 `/etc/apt/sources.list.d/linbox.sources` with `Signed-By`, channel selection. |
| `linbox-base` | meta + config | Depends: keyring, repository, `linbox-system`; OS identity (D7); system defaults (e.g. `non-free-firmware` in sources, zram, fstrim). Shared by all editions. |
| `linbox-system` | app | The `linbox` CLI (version, doctor, hardware, update, recovery, support) and the config-migration framework. |
| `linbox-branding` | data | Wallpapers, colour scheme, icons, fonts, Plymouth and GRUB themes, desktop-neutral assets. |
| `linbox-desktop-settings` | config | *(Plasma, per D3)* Linbox Global Theme, system-wide defaults in `/etc/xdg` (kdeglobals, kwinrc, panel layout, shortcuts), Konsole profile, SDDM theme. |
| `linbox-desktop` | meta | Default edition: Depends `linbox-base`, `linbox-branding`, `linbox-desktop-settings`, a curated Plasma subset (not `task-kde-desktop`), and Xwayland. |
| `linbox-installer-config` | config | Calamares settings, branding, slideshow. Live session only. |
| `linbox-developer` | app | Developer Setup GUI plus profile definitions (Phase 3). |
| `linbox-hardware` | data + config | Per-model quirks keyed on DMI, the hardware DB snapshot (Phase 4). |
| *(future)* `linbox-desktop-focus` | meta | Hyprland edition, reusing `linbox-base` and `linbox-branding`. |

### Configuration management rules

1. **System defaults, not home directories.** Desktop defaults go in
   `/etc/xdg` (both Plasma and Xfce honour `XDG_CONFIG_DIRS`). User settings
   in `~/.config` always win and are never touched by package upgrades.
2. **Migrations are explicit and versioned.** When a default must change for
   existing users, `linbox-system` ships a numbered migration. It runs per user
   at login, is idempotent, records its state in
   `~/.local/state/linbox/migrations`, backs up any file it changes, and never
   deletes user data.
3. **conffile hygiene.** Files under `/etc` are dpkg conffiles. Local admin
   edits trigger dpkg's prompt and are never silently overwritten. Files owned
   by other packages are changed only through `dpkg-divert`, documented in
   `docs/system-modifications.md` (created in M2).
4. **No fragile scripts.** If a setting can't be a packaged default, it goes
   through rule 2.

## 6. Repository and channel strategy

- **Channels** are APT suites on `apt.linbox.in`: **`trixie`** (stable) and
  **`trixie-testing`**. These are Linbox suites, unrelated to Debian's own
  "testing" distribution. Packages are built once, land in testing, and are
  **promoted** (copied) to stable unchanged. There are no rebuilds between
  channels.
- **Hosting (D5):** **reprepro** run by CI. The reprepro state (`conf/`,
  `db/`, `dists/`, `pool/`) lives on the `apt-repo` branch; the public part is
  deployed to **GitHub Pages** with the custom domain `apt.linbox.in`. Pages
  is free for public repositories; its limits (about 1 GB per site, a soft
  100 GB/month of traffic, 100 MB per file) fit a repository that holds only
  Linbox's own small packages, because Debian packages come from Debian. If
  the limits are reached, the same tree moves to object storage behind the
  same domain. Trust does not depend on the host: APT checks every `Release`
  file against the Linbox archive key. The signing subkey lives in CI secrets
  and the primary key stays offline with the maintainer. Details:
  [apt-repository.md](apt-repository.md).
- **Debian's archive is used directly** (`deb.debian.org`,
  `security.debian.org`). We don't mirror or filter it.
- **Third-party repositories** are never enabled in the base image. Developer
  Setup may add vendor repos (Docker, VS Code, Mozilla …) only when the user
  picks that profile, with the key pinned by fingerprint and an uninstall
  path.

## 7. Versioning

Linbox no longer shares a version number with its base (Debian is "13"), so
it has its own:

| Thing | Scheme | Example |
|---|---|---|
| OS major | One per Debian base | **Linbox OS 1** = trixie; **2** = forky (Debian 14) |
| OS point release | Bumped for each ISO respin | `1.0`, `1.1` |
| Pre-releases | `-devN`, `-previewN`, `-rcN` | `1.0-preview1` |
| Image build ID | `YYYYMMDD.N` | `linbox-os-1.0-preview1-20261205.1-amd64.iso` |
| Linbox packages | SemVer-ish Debian native | `linbox-system 0.3.0` |
| Config migrations | Monotonic integers per package | `linbox-desktop-settings/0004-…` |

Every ISO ships `/usr/share/linbox/build-info.json`. It records:

- the build ID
- the git commit
- the Debian snapshot timestamp
- the Linbox package versions
- the builder environment

The ISO is published with `SHA256SUMS`, which is signed, and a full package
manifest.

## 8. Developer experience, CLI and updates (Phase 3 outline)

- **`linbox` CLI:** Python 3, standard library only (D13). It has `--json`
  output for support engineers. Unimplemented commands exit non-zero with a
  clear message; nothing reports false success.
- **Developer Setup:** a Qt/KDE GUI (matching Plasma, per D3) that runs
  **declarative profiles**. Each step says what it installs, where from, and
  how to undo it.
  - Privileged steps go through `pkexec` with narrow polkit actions.
  - User-space toolchains (fnm, uv, SDKMAN, Flutter) install as the user.
  - Downloads are verified. There is no `curl | sudo bash`.
- **Updates:** `linbox update` wraps apt with pre-flight checks (disk, repo
  health, held/broken packages, AC power) and a post-update migration run.
  Debian's `unattended-upgrades` is enabled for security updates only. There
  is no automatic destructive cleanup.

## 9. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R1 | **Plasma is heavier than the original XFCE target.** | Ship a curated Plasma subset, not `task-kde-desktop`. Measure idle RAM and boot time in M2 and set a budget. Disable Baloo file indexing by default if it costs too much on 8 GB machines. |
| R2 | **Some developer tools still need X11.** | Keep Xwayland (D2). Test Android Studio + emulator, JetBrains IDEs, VS Code and Flutter in M3. |
| R3 | **Newer hardware vs Debian stable's 6.12 kernel and its frozen Mesa/firmware.** | Refurbished business laptops are mostly older, which suits it well. Use backports per model only with a test. Track in the hardware DB. |
| R4 | **Installer gaps.** Calamares has no unattended mode and no TPM unlock, and Wayland-only live sessions are unverified. | Validate in M1. Factory flow per D11. |
| R5 | **Debian's 2-year release cadence.** Trixie's regular support ends around 2028, before LTS takes over. | Plan the Linbox OS 2 (forky) rebase when forky releases. Test upgrades between majors in CI. |
| R6 | **Build environment.** The primary workstation is Windows. | Build in CI (privileged Debian container) plus a Linux VM or WSL2, validated in M1. |
| R7 | **Intel IPU6 / OV02C10 webcams** may not work on Debian stable out of the box. | Hardware DB marks them `untested` until proven. No support claim without a tested report. |
| R8 | **Changing `/etc/os-release` `ID`** breaks third-party install docs that use `$ID`/`$VERSION_CODENAME` (e.g. Docker's repo URL). | D7. Developer Setup maps Linbox → Debian when adding vendor repos. |
| R9 | **Trademarks.** Debian's policy allows "based on Debian", but the Debian logo and the KDE/Xfce marks need care. | D12: review before the first public ISO. |
| R10 | *(Found in M1.)* **Debian's `sddm` package Depends on `xserver-xorg \| xserver`**, even though its greeter runs on Wayland. | M1 satisfies the dependency with `xserver-xephyr`. It's a small nested X server that is installed but never started, and there is no Xorg server or X11 session. The build hook fails if Xorg appears. Alternatives if zero X server binaries are required: greetd with a Wayland greeter, or a Linbox-patched `sddm`. Revisit when Debian relaxes the dependency or Plasma's new login manager reaches Debian. |

*Removed from revision 1:* the Ubuntu "universe" security-coverage risk.
Debian's security team covers the whole `main` archive, including the desktop.
Also removed: the Canonical trademark risk.

## 10. Decisions

| ID | Decision | Status / recommendation | Alternatives |
|---|---|---|---|
| **D1** | Base distribution | **Decided (maintainer, 2026-11-22):** Debian 13 trixie, `main` + `non-free-firmware` | Ubuntu 26.04 / Xubuntu (revision 1) |
| **D2** | Display server | **Decided (maintainer, 2026-11-22):** Wayland only, no Xorg. **Approved:** Xwayland kept for app compatibility. | No Xwayland: breaks X11-only developer tools |
| **D3** | Desktop environment | **Decided (maintainer, 2026-11-22):** **KDE Plasma 6 on Wayland** | Xfce 4.20 on labwc (experimental); GNOME 48; custom compositor stack |
| **D4** | ISO build tool + installer | **Approved (2026-11-22):** live-build + Calamares | debian-installer + debian-cd; mkosi/debos (no installer); remastering Debian's live ISO |
| **D5** | Package hosting | **Approved (2026-11-22), hosting amended (maintainer, 2026-11-23):** reprepro in CI → **GitHub Pages** at apt.linbox.in (free, no card on file). Move to object storage if Pages limits are reached; the URL stays the same. | openSUSE Build Service; aptly; Cloudflare R2 (needs a card on file and DNS on Cloudflare); S3 + CloudFront (paid egress) |
| **D6** | Channel model | **Approved (2026-11-22):** `trixie` and `trixie-testing`, promotion without rebuild | Single channel plus tags |
| **D7** | OS identity | **Approved (2026-11-22):** `ID=linbox`, `ID_LIKE=debian`, keep `VERSION_CODENAME=trixie` | Keep `ID=debian` and change only `NAME`/`PRETTY_NAME` |
| **D8** | App delivery | **Approved (2026-11-22):** Debian debs only in base, no snapd, Firefox ESR. Flatpak/Flathub opt-in via Developer Setup. | Flathub enabled by default; Mozilla's APT repo for current Firefox |
| **D9** | Filesystem and recovery | **Approved (2026-11-22):** ext4 default now. Calamares supports Btrfs subvolumes, so evaluate **Btrfs + Snapper as an opt-in** in M5 (§11). | Btrfs + Snapper default from 1.0 |
| **D10** | Kernel policy | **Approved (2026-11-22):** Debian stable kernel. Backports only per tested model. | Backports kernel for everyone (fresher, less tested) |
| **D11** | Factory provisioning | **Approved (2026-11-22):** Decide in M4: d-i preseed vs a preinstalled mkosi/debos image | — |
| **D12** | Trademark review before the first public ISO | **Approved (2026-11-22):** Yes: blocking for the public preview | — |
| **D13** | CLI language | **Approved (2026-11-22):** Python 3, stdlib only | Bash; Go/Rust |

## 11. Recovery and snapshots

| Option | Pros | Cons |
|---|---|---|
| **ext4 + apt discipline + recovery docs** | Simplest and most tested | No rollback; recovery means fixing forward or reinstalling `/` while keeping `/home` |
| ext4 + Timeshift (rsync) | Works on ext4 | Slow, space-hungry, not atomic |
| **Btrfs + Snapper (+ grub-btrfs)** | Atomic pre/post-apt snapshots, boot into a snapshot. Calamares can create the subvolume layout. | More support complexity; `/boot` and kernel-snapshot mismatch need care |
| LVM thin snapshots | Filesystem-agnostic | Complex for users |
| A/B or image-based | Strongest guarantees | Fights APT's model; very high cost |

**Recommendation:** ext4 for 1.0. `linbox update` has pre- and post-hooks so a
snapshot backend can plug in. Btrfs + Snapper is the leading candidate for an
opt-in in 1.x, and possibly the default for Linbox OS 2, after an M5
evaluation.

## 12. Initial repository structure

```
linbox-os/
├── README.md  LICENSE  CONTRIBUTING.md
├── docs/                    architecture, build options, build guide, hardware, release, security, roadmap
├── build/
│   ├── manifests/           image manifest (Debian snapshot pin, packages per edition)
│   ├── live-build/          lb config tree: package lists, hooks, includes (M1)
│   ├── installer/           Calamares config sources; factory preseed (M2/M4)
│   └── scripts/             build entry points (M1)
├── packages/                one directory per Debian source package (M2+)
├── desktop/                 design sources (theme, wallpaper SVGs, shortcuts)
├── hardware/
│   ├── compatibility/       hardware DB (one YAML per model) + schema
│   └── diagnostics/         collectors used by `linbox hardware` (Phase 4)
├── tests/                   VM install/upgrade/smoke tests
└── tools/                   developer utilities (lint, validation)
```

`applications/` (Developer Setup) arrives in Phase 3. Build artefacts go only
to the git-ignored `out/`, `work/` and `cache/`.
