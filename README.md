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

See `docs/` (coming in Phase 1) for the architecture proposal, build guide and
hardware compatibility strategy.

## License

Linbox OS's own source — build scripts, packaging, configuration, tools and
documentation in this repository — is licensed under the
[Apache License 2.0](LICENSE).

Ubuntu packages and other third-party software included in Linbox OS images
keep their own upstream licences.
