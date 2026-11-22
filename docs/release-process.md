# Release process

**Status:** Proposed. Versioning is defined in
[architecture.md §7](architecture.md#7-versioning).

## Channels

| Channel | APT suite | Who | Contents |
|---|---|---|---|
| testing | `trixie-testing` | Linbox team, early adopters | Every merged package change, after CI |
| stable | `trixie` | All users, shipped laptops | Packages promoted unchanged from testing |

Debian's own archive (`deb.debian.org`, `security.debian.org`) is never mirrored
or filtered. Users get Debian security updates directly from Debian. Linbox suites are unrelated to Debian's own "testing" distribution.

## Package flow

1. A PR is merged into `main`. CI builds the package and lints it
   (`lintian`, `shellcheck`, tests).
2. A version is tagged (`<package>/<version>`), and the source is uploaded to
   **testing**.
3. Validation: a fresh VM install plus an upgrade from the current stable,
   then `linbox doctor`, plus a manual check for desktop-visible changes.
4. **Promote** the package to stable by copying it without rebuilding. Record
   it in the channel changelog.
5. **Rollback** means uploading a higher version that reverts the change.
   We never delete a published version.

## ISO releases

1. Freeze: stable contains the intended package set.
2. Build the ISO from a tagged commit (`release/1.0-previewN`). CI produces
   the ISO, SHA256SUMS, build-info and manifest.
3. Release checklist (in a `tests/` doc):
   - UEFI + Secure Boot install in a VM
   - install on at least one supported laptop
   - upgrade from the previous release
   - offline install
4. Publish:
   - signed `SHA256SUMS` (Linbox release key)
   - release notes covering changes, known issues, supported hardware and
     upgrade notes
   - git tag
5. Failures found after release go into the release notes' known-issues list
   and are fixed through package updates. Re-spin the ISO only for
   installer or boot problems.

## Failure reporting

`linbox support` (Phase 3) collects a **local** redacted bundle the user can
review and attach. Nothing is sent automatically (see
[security.md](security.md)).
