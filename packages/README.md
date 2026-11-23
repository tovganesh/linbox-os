# Debian source packages

One directory per source package. The planned set and each package's responsibility are in [docs/architecture.md §5](../docs/architecture.md#5-package-architecture). Build them with `build/scripts/build-packages` (inside a Debian 13 container).
Every change to a package needs a version bump in `debian/changelog`; publishing is
described in [docs/apt-repository.md](../docs/apt-repository.md).
