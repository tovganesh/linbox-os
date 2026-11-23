# Build guide

Status: **Milestone M1 (build spike).** The ISO builds from source control.
Linbox branding and the real `linbox-*` packages arrive in M2.

## What you need

- **Docker** with privileged containers: Docker Engine on Linux, or Docker
  Desktop on Windows or macOS. The build itself runs inside a `debian:trixie`
  container, so nothing is installed on your machine.
- About **25 GB** free for the Docker volume `linbox-os-work`, which holds the
  chroot and package downloads.
- A good network connection. Every package comes from
  `snapshot.debian.org`, which is slower than a normal mirror; expect 30–90
  minutes for the first build.

## Build

```sh
./build/scripts/build-in-docker
```

On Windows, run it from Git Bash or WSL. Environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `BUILD_ID` | `YYYYMMDD.local` | Goes into the ISO name and `build-info.json` |
| `BUILD_IMAGE` | `debian:trixie` | Container image that runs the build |
| `BUILD_VOLUME` | `linbox-os-work` | Docker volume used as scratch space |

The output goes to `out/` (git-ignored):

```
out/linbox-os-1.0-dev-<BUILD_ID>-amd64.iso             hybrid ISO (UEFI + BIOS)
out/linbox-os-1.0-dev-<BUILD_ID>-amd64.packages        installed package manifest
out/linbox-os-1.0-dev-<BUILD_ID>-amd64.build-info.json build metadata (also inside the image)
out/linbox-os-1.0-dev-<BUILD_ID>-amd64.SHA256SUMS
out/linbox-os-1.0-dev-<BUILD_ID>-amd64.build.log
```

To reclaim the scratch space, run `docker volume rm linbox-os-work`.

## How it works

[`build/scripts/build-iso`](../build/scripts/build-iso) runs as root inside
the container:

1. **Pin the inputs.** It reads `base.snapshot` from
   [`build/manifests/linbox-1.yaml`](../build/manifests/linbox-1.yaml) and
   points the container's own apt at that `snapshot.debian.org` timestamp, so
   live-build and the other tools are pinned too.
2. **Build the Linbox packages.** It builds every `packages/*/debian` with
   `dpkg-buildpackage` in a copy under `/work`.
3. **Configure live-build.** It runs `lb config` with these settings:
   - Debian trixie, `main non-free-firmware`
   - snapshot mirrors for the build; `deb.debian.org` and
     `security.debian.org` for the installed system
   - security and updates enabled
   - no debian-installer (Calamares is the installer)
   - Secure Boot enabled

   It then overlays
   [`build/live-build/config/`](../build/live-build/config) and adds the
   Linbox `.deb`s to `config/packages.chroot/`.
4. **Build.** `lb build` produces the hybrid ISO. The hook
   `9000-linbox-assert-no-xorg` fails the build if any Xorg server or X11
   session package is installed (decision D2).
5. **Artefacts.** The ISO, the manifest, the build info, the checksums and the
   log are copied to `out/`.

It never writes to the source tree, and the container mounts it read-only.

## Checking a package selection before building

[`tools/dep-closure.py`](../tools/dep-closure.py) approximates apt's
dependency closure from a `Packages` index. It answers questions like "which
package pulls in Xorg?":

```sh
curl -fsSL https://snapshot.debian.org/archive/debian/<ts>/dists/trixie/main/binary-amd64/Packages.xz | xz -d > Packages
python3 tools/dep-closure.py Packages --recommends --why '^xserver-xorg' kde-plasma-desktop sddm xserver-xorg-
```

## Testing

See [tests/README.md](../tests/README.md). CI builds the ISO twice and
compares the package manifests. It then boots the ISO in QEMU with Secure
Boot enforced and checks the live Plasma Wayland session.
