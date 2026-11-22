# Image-building approaches for Ubuntu 26.04 LTS

**Status:** Proposed. This feeds decision **D2** in [architecture.md](architecture.md).
**Researched:** 2026-11-22.

## What we need from the tool

1. **Reproducible from git.** The same commit plus the same pinned inputs
   gives an equivalent image, buildable in CI.
2. **Keeps the stock Ubuntu installer working.** That means the Flutter UI on
   subiquity, its layered squashfs, TPM-FDE support, and autoinstall.
3. **Low maintenance.** Linbox is a small team, and every release cycle must
   not mean re-learning the image tool.
4. **Keeps the Secure Boot chain intact.** The tool must not re-sign shim,
   GRUB or the kernel.
5. **Supported or documented by Canonical**, where possible.

## Candidates

### A. livefs-editor: remaster a pinned Xubuntu ISO *(recommended)*

Canonical's image cookbook calls
[livefs-editor](https://github.com/mwhudson/livefs-editor) "the tool of choice"
for customising an existing live-installer ISO. It recommends it over patching
livecd-rootfs or ubuntu-cdimage, which the cookbook calls tedious and
error-prone. It's driven by a YAML action file. Documented actions include
copying files in, `install-packages`, removing pool packages and
`replace-kernel`.

- **Pros:** small, declarative, scriptable in CI. It reuses the exact,
  flavour-tested Xubuntu ISO, installer and layer structure. Inputs are
  pinned by SHA-256 and verified against Canonical's GPG-signed `SHA256SUMS`.
  Fast builds, measured in minutes rather than hours.
- **Cons:** our image inherits upstream's choices and we can only add or
  remove on top. Its behaviour with the **layered Desktop installer ISO** is
  undocumented, since the cookbook example is a Server ISO. We need to prove
  that packages land in the layer the installer copies to disk, not just the
  live session (risk R5). It's maintained by a Canonical engineer, but it's a
  small project.
- **Maintenance:** low, as long as Xubuntu keeps publishing ISOs. The upstream
  pin is bumped deliberately for each point release.

### B. livecd-rootfs: build like Canonical does

The cookbook says livecd-rootfs is what Canonical uses for preinstalled and
installer images "as of 2026". It documents
`PROJECT=xubuntu SUBPROJECT=minimal SUITE=resolute` with the
`auto/clean → auto/config → auto/build` flow. Official builds run as livefs
builds on Launchpad, orchestrated by `ubuntu-cdimage`.

- **Pros:** the real pipeline. We can control seeds, layers and every package
  from first principles, and it builds exactly the image types Ubuntu ships.
- **Cons:** a Canonical engineer describes direct use as extremely
  challenging; it isn't designed as a single script. The full ISO assembly
  also involves `ubuntu-cdimage`/`debian-cd`. There are significant changes
  between releases, the build is slow and heavy, and it must run on a host of
  the same series. A "craft" replacement is being developed, so the tool
  itself will change under us.
- **Maintenance:** high. It's the right tool if we later need our own seeds
  or layers, or if remastering proves insufficient.

### C. Cubic

A GUI wizard that chroots into an extracted ISO.

- **Pros:** approachable for one-off customisation.
- **Cons:** interactive, so not reproducible from git or CI. It's a
  third-party tool, and its 26.04 status is unverified (the community reports
  library issues). **Rejected** as a primary tool. Fine for prototyping a
  look.

### D. debootstrap / live-build / mkosi from scratch, plus our own installer (e.g. Calamares)

- **Pros:** total control, and well-understood Debian tooling.
- **Cons:** we lose the Ubuntu installer (TPM-FDE, autoinstall, subiquity's
  storage handling), so we'd own an installer, boot-chain assembly and Secure
  Boot plumbing. That's the largest ongoing cost of any option, for no
  user-visible benefit in Milestone 1. **Rejected.**

### E. ubuntu-image (`classic`)

Its image-definition YAML has an `iso` artefact type in the schema, but the
documented examples produce disk images (`.img`). It's aimed at preinstalled
and gadget-based images.

- **Assessment:** a possible future path for **preinstalled factory disk
  images** for Linbox laptops. It's not a documented route to a desktop
  installer ISO today. **Not selected** for Milestone 1; revisit for factory
  imaging.

### F. Autoinstall-only: stock Xubuntu ISO plus an autoinstall file that adds the Linbox repo and packages

- **Pros:** no image modification at all.
- **Cons:** needs network at install time, and there's no Linbox branding in
  the live session or installer. It's not a distributable product image.
- **Assessment:** not a distribution strategy, but **is** our factory
  provisioning mechanism (see architecture §4).

## Comparison

| | Reproducible | Keeps stock installer | Maintenance | Canonical-documented | Speed |
|---|---|---|---|---|---|
| **A. livefs-editor** | ✅ | ✅ (to be proven on desktop ISO) | Low | ✅ (customise) | Fast |
| B. livecd-rootfs | ✅ | ✅ | High | ✅ (build) | Slow |
| C. Cubic | ❌ | ✅ | Medium | ❌ | Medium |
| D. From scratch | ✅ | ❌ | Very high | ❌ | Medium |
| E. ubuntu-image | ✅ | n/a (no installer ISO) | Medium | ✅ (preinstalled) | Medium |
| F. Autoinstall only | ✅ | ✅ | Low | ✅ | — |

## Recommendation

Use **A (livefs-editor) as the primary approach**, gated by a Phase 2 spike
with these exit criteria:

1. A remastered Xubuntu 26.04.1 Minimal ISO boots in UEFI mode with Secure
   Boot on, in a VM.
2. The installer installs a system that contains the Linbox packages.
3. The installed system boots and `apt` resolves without errors.

If criterion 2 fails because of layering, switch to **B (livecd-rootfs,
`PROJECT=xubuntu`)**. Because all customisation lives in packages (see
architecture §1), the switch only changes `build/`. Separately, keep
**F (autoinstall)** for factory installs and **E (ubuntu-image)** under
review for preinstalled factory images.

## Sources

- [Image cookbook: create installer image](https://ubuntu.com/hardware/docs/image-cookbook/howto/images/create_installer_image/)
- [Image cookbook: customise installer image](https://ubuntu.com/hardware/docs/image-cookbook/howto/images/customize_installer_image/)
- [How Ubuntu is made: image builds](https://ubuntu.com/project/docs/how-ubuntu-is-made/processes/image-builds/)
- [Discourse: How to create my own bootable image?](https://discourse.ubuntu.com/t/how-to-create-my-own-bootable-image/77158)
- [ubuntu-image classic examples](https://canonical-subiquity.readthedocs-hosted.com/en/latest/howto/ubuntu-image-classic-examples.html)
- [ubuntu-desktop-provision](https://github.com/canonical/ubuntu-desktop-provision)
- [Xubuntu 26.04 release notes](https://xubuntu.org/releasedocs/26.04/release-notes/)
