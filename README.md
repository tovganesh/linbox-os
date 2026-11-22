# Linbox OS

A developer-focused Linux distribution by [Linbox](https://linbox.in), built to power
professionally refurbished business laptops.

**Status:** Phase 1 — architecture and foundation. Nothing here is buildable yet.

## Direction (initial, pending architecture review)

- Base: Ubuntu 26.04 LTS (amd64)
- Desktop: XFCE on X11
- Packages: APT, Ubuntu archive + a Linbox repository
- Filesystem / boot: ext4, GRUB, systemd
- Audience: developers and technical professionals

## Documentation

- [Architecture proposal](docs/architecture.md): design, packages, risks and
  **decisions awaiting approval**
- [Image-build options](docs/image-build-options.md): how the ISO is built,
  and why
- [Milestone plan](docs/roadmap.md)
- [Hardware compatibility](docs/hardware-compatibility.md)
- [Build guide](docs/build-guide.md) · [Release process](docs/release-process.md) · [Security](docs/security.md)
- [Contributing](CONTRIBUTING.md)

## License

Linbox OS's own source — build scripts, packaging, configuration, tools and
documentation in this repository — is licensed under the
[Apache License 2.0](LICENSE).

Ubuntu packages and other third-party software included in Linbox OS images
keep their own upstream licences.
