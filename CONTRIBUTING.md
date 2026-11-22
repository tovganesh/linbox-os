# Contributing to Linbox OS

Linbox OS is developed in the open. Contributions are welcome.

## Workflow

- `main` is protected by convention: **every change lands through a pull
  request**, including changes from maintainers.
- Branch names: `<area>/<short-topic>`, e.g. `packages/linbox-system-doctor`,
  `docs/hardware-thinkpad-t14`.
- Keep the project buildable at every merge. Update the docs in the same PR
  when behaviour or architecture changes.
- Architectural changes update [docs/architecture.md](docs/architecture.md)
  (decision table) and are discussed in the PR before implementation.

## Standards

- Follow [docs/security.md](docs/security.md).
- Shell: `shellcheck`-clean, `set -euo pipefail`, no unquoted expansions.
- Line endings are LF (enforced by `.gitattributes`).
- Don't claim hardware or features work without a test. Hardware entries need
  test evidence (see [docs/hardware-compatibility.md](docs/hardware-compatibility.md)).

## Licence

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
