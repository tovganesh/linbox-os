# Build entry points

Build scripts. They must pass `shellcheck` and never write to the source tree.
All except `build-in-docker` run as root inside a throwaway `debian:trixie` container.

| Script | Purpose |
|---|---|
| `build-in-docker` | Host entry point: runs `build-iso` in a container ([build guide](../../docs/build-guide.md)) |
| `build-iso` | Builds the live ISO from the manifest |
| `setup-build-env` | Pins the container's apt to the manifest snapshot and installs build tools |
| `build-packages` | Builds `packages/*` into `.deb`s |
| `publish-apt` | Adds `.deb`s to the APT repository, signs it, assembles the site |
| `promote-apt` | Copies a tested version from `trixie-testing` to `trixie` |
| `ci-apt` | CI entry point for the APT workflow ([apt-repository.md](../../docs/apt-repository.md)) |
