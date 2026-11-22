# Image-building approaches for a Debian 13 base

**Status:** Approved (D4, 2026-11-22). This feeds decision **D4** in
[architecture.md](architecture.md). **Researched:** 2026-11-22.

*Revision 2: the base changed from Ubuntu 26.04 to Debian 13 "trixie". The
Ubuntu options (livecd-rootfs, livefs-editor, ubuntu-image, the subiquity
installer) no longer apply.*

## What we need from the tool

1. **Reproducible from git.** The same commit plus the same pinned inputs
   gives an equivalent image, buildable in CI.
2. **A graphical installer** for end users that supports encryption and
   sensible partitioning, and works in a Wayland-only live session.
3. **Low maintenance** for a small team.
4. **Keeps Debian's Secure Boot chain intact** (shim → GRUB → kernel, all
   signed by Debian).
5. **The tool Debian itself uses**, where possible.

## Candidates

### A. live-build + Calamares *(recommended)*

live-build is Debian's own live-system builder, maintained by the Debian
Live team. The official Debian live ISOs are built with it, using configs in
the live team's `live-setup` repository, and they ship Calamares as the
installer.

- **Pros:**
  - The same toolchain as official Debian live images, so we can start from
    their published configs.
  - Configuration is a plain directory tree (package lists, chroot hooks,
    `includes.chroot`), which fits git well.
  - Builds run in a Debian container.
  - Debian's reproducible-builds work already rebuilds these images: the
    squashfs reproduces, the full ISO not yet.
  - Pointing it at `snapshot.debian.org` pins every package version.
  - Calamares provides LUKS encryption, Btrfs subvolume layouts and
    branding/slideshow modules.
- **Cons:**
  - live-build's documentation is dated.
  - Calamares is a separate upstream project (packaged in Debian) that we'll
    configure heavily.
  - Calamares has no unattended mode and no TPM unlock.
  - Calamares in a Wayland-only live session needs M1 validation.
- **Maintenance:** low to medium. The config is ours, and the tool is
  Debian-packaged and stable across releases.

### B. debian-installer (d-i) + debian-cd, with preseed

The official Debian installer ISO, customised with a preseed file and extra
packages.

- **Pros:** the most battle-tested Debian installer. **Fully unattended with
  preseed**, which is ideal for factory installs. Secure Boot supported.
- **Cons:** no live session, so users can't try the OS first and the first
  impression is weaker. Customising debian-cd is heavier than live-build.
- **Assessment:** not the consumer ISO. It's the **leading candidate for
  factory provisioning** (D11).

### C. mkosi (systemd project)

A declarative image builder (`mkosi.conf`) that produces disk images,
including signed UKIs, in a well-maintained, reproducible-minded way.

- **Pros:** modern, declarative, fast; excellent for **VM test images and
  preinstalled disk images**.
- **Cons:** no end-user installer ISO. Integrating an installer means
  building that half ourselves.
- **Assessment:** a strong tool for **CI test VMs** and a **factory
  preinstalled image** (D11). Not the consumer ISO.

### D. debos (Collabora)

A YAML-recipe image builder, widely used for embedded and preinstalled images.

- **Assessment:** similar role to mkosi. It's an alternative for preinstalled
  images; mkosi is preferred for the systemd/UKI direction.

### E. Remastering the official Debian Live ISO

- **Assessment:** unnecessary. Unlike Ubuntu's pipeline, Debian's own build
  tool (A) is approachable, and remastering hides changes from the build
  config. **Rejected.**

### F. Third-party remaster tools (penguins-eggs, refracta, Cubic-like GUIs)

- **Assessment:** they snapshot a running system or are interactive, so
  they're not reproducible from git. **Rejected.**

## Comparison

| | Reproducible | Live session + GUI installer | Unattended install | Maintenance | Used by Debian |
|---|---|---|---|---|---|
| **A. live-build + Calamares** | ✅ (+ snapshot.debian.org) | ✅ | ❌ | Low–medium | ✅ live ISOs |
| B. d-i + preseed | ✅ | ❌ | ✅ | Medium | ✅ installer ISOs |
| C. mkosi | ✅ | ❌ | n/a (image) | Low | — |
| D. debos | ✅ | ❌ | n/a (image) | Low | — |
| E. Remaster live ISO | ⚠️ | ✅ | ❌ | Medium | — |
| F. Snapshot tools | ❌ | ✅ | ❌ | Medium | — |

## Recommendation

Use **A (live-build + Calamares)** for the Linbox OS ISO. The **M1 spike** has
these exit criteria:

1. Builds in a Debian 13 container from `snapshot.debian.org` pinned inputs.
2. Boots in UEFI mode with Secure Boot on (QEMU/OVMF) into a Wayland-only
   live session.
3. Calamares installs to disk. The installed system boots, contains the Linbox
   test package, and `apt` resolves cleanly.
4. Two builds of the same commit produce identical package manifests.

Use **mkosi** for CI test VMs. Decide between **d-i preseed** and a **mkosi
preinstalled image** for factory provisioning in M4.

## Sources

- [The Debian Live Project](https://www.debian.org/devel/debian-live/)
- [Debian live install images](https://www.debian.org/CD/live/)
- [Debian live team (Salsa)](https://salsa.debian.org/live-team)
- [Reproducible live images (Debian wiki)](https://wiki.debian.org/ReproducibleInstalls/LiveImages)
- [What's new in Debian 13](https://www.debian.org/releases/stable/release-notes/whats-new.html)
