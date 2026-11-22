# Security policy and engineering rules

## Reporting a vulnerability

Until a dedicated address is published, report vulnerabilities privately
through GitHub's **Security → Report a vulnerability** on this repository.
Please don't open public issues for security problems.

## Rules for everything in this repository

- **Upstream first.** Prefer Ubuntu archive packages. Each third-party
  repository needs an architecture decision and is never enabled in the base
  image.
- **Verify every download** against a pinned checksum or a pinned signing
  key fingerprint. Never `curl | sh`, and never run remote scripts as root.
- **Least privilege.** User-space toolchains install as the user. Privileged
  actions go through narrow polkit actions or explicit `sudo`, with the
  command shown first.
- **The Secure Boot chain is untouched.** We use Ubuntu's signed shim, GRUB
  and kernel. We don't disable Secure Boot, and we avoid DKMS modules that
  need MOK enrollment.
- **No telemetry without explicit opt-in.** Diagnostics bundles are created
  locally and shared only by the user.
- **No secrets in git.** Signing keys live offline or in CI secret storage.
  Only public keys are committed.
- **Never overwrite user data.** Package upgrades don't touch `$HOME`.
  Migrations back up any file they change and never delete it.
- **No automatic destructive cleanup.**
- **Idempotent, documented changes.** Every system modification is listed in
  `docs/system-modifications.md` (created with the first package that
  modifies the system).
- **Linting.** All shell scripts pass `shellcheck`. Packages pass `lintian`.
