# Linbox APT repository

**Status:** M2. Decision D5 (amended 2026-11-23): reprepro in CI, served by
GitHub Pages at `https://apt.linbox.in/`.

The repository holds **only Linbox's own packages** (`linbox-*`). Debian
packages always come from Debian's mirrors.

## How it fits together

| Piece | Where |
|---|---|
| Package sources | `packages/<name>/` on `main` |
| reprepro config | [`build/apt/conf/`](../build/apt/conf) |
| reprepro state (`conf/ db/ dists/ pool/`) | the `apt-repo` branch, written only by CI |
| Public site | GitHub Pages, deployed by [`apt.yml`](../.github/workflows/apt.yml) |
| Public archive key | `packages/linbox-keyring/keys/*.asc`, shipped as `/usr/share/keyrings/linbox-archive-keyring.asc` |
| Secret signing subkey | GitHub secrets `LINBOX_APT_SIGNING_KEY` and `LINBOX_APT_SIGNING_PASSPHRASE` |
| Primary key | offline, with the maintainer |

Installed systems get the repository from the `linbox-repository` package:
`/etc/apt/sources.list.d/linbox.sources`, with `Signed-By` pointing at the
Linbox keyring. The Linbox key is trusted for this repository only.

## Publishing

1. Change a package and **bump its version** in `debian/changelog`.
2. Open a PR. The `APT / test` job runs
   [`tests/apt/test-repo`](../tests/apt/test-repo). It builds a repository with
   a throwaway key, then checks signing, reproducibility, version-bump
   enforcement, `apt update` on Debian 13, and promotion.
3. Merge. `APT / publish` rebuilds every package and adds new versions to
   **`trixie-testing`**. It signs the `Release` files, checks the signatures
   against the keys in `linbox-keyring`, commits the state to `apt-repo` and
   deploys the site.

Rebuilds of unchanged sources are bit-identical, so they are no-ops. A
package whose content changed **without** a version bump fails the publish
job. Published versions are never deleted: reprepro keeps old `.deb`s in the
pool (`keepunreferencedfiles`). To roll back, publish a higher version.

## Promoting to stable

Actions → **APT** → *Run workflow* on `main`. Enter the package name and the
exact version that is in `trixie-testing`. The job copies that same `.deb`
into **`trixie`**, with no rebuild (D6). It refuses:

- a version that is not the current one in testing
- a version that is not newer than what stable already has

Do this only after the validation in [release-process.md](release-process.md).

## One-time setup (maintainer)

### 1. Create the archive key

On a trusted machine, from this repository (Git Bash on Windows works):

```sh
tools/make-archive-key /path/to/offline/storage
```

It asks for a passphrase. It writes the **public** key to
`packages/linbox-keyring/keys/linbox-archive-<year>.asc`; commit that file.
It writes these secret files to the offline directory, never into the
checkout:

- the primary key
- a revocation certificate
- the signing subkey

The layout is an ed25519 certify-only primary that expires in 5 years, plus
an ed25519 signing subkey that expires in 2 years.

### 2. Give CI the signing subkey

As the `tovganesh` GitHub account:

```sh
gh secret set LINBOX_APT_SIGNING_KEY --repo tovganesh/linbox-os < /path/to/offline/storage/linbox-archive-<year>-signing-subkey.asc
gh secret set LINBOX_APT_SIGNING_PASSPHRASE --repo tovganesh/linbox-os
```

Then delete the `-signing-subkey.asc` file. The primary-key file can recreate
it.

### 3. Turn on GitHub Pages

Repository **Settings → Pages**:

- **Source:** GitHub Actions
- **Custom domain:** `apt.linbox.in`
- **Enforce HTTPS:** on, once the certificate is issued

### 4. DNS

At the DNS provider for `linbox.in`, add:

```
apt.linbox.in.   CNAME   tovganesh.github.io.
```

Optionally, verify the domain under GitHub account settings → Pages, so that
no other account can claim it.

## Key maintenance

- **Signing subkey expiry (every 2 years):** with the offline primary key, run
  `gpg --quick-set-expire <primary-fpr> 2y <subkey-fpr>`. Commit the updated
  public key, bump `linbox-keyring`, and update the CI secret.
- **Rotation:** add the new public key next to the old one in
  `packages/linbox-keyring/keys/` and release `linbox-keyring`. Switch CI to
  the new subkey only after that version has reached stable. Remove the old
  key in a later release.
- **Compromise:** publish the revocation certificate. Then ship a
  `linbox-keyring` update signed with the replacement key; users need a manual
  step if the old key can no longer be trusted. Rotation ahead of time avoids
  this.

## Limits

GitHub Pages limits are about 1 GB per site, a soft 100 GB a month of
traffic, and 100 MB per file. Linbox packages are kilobytes to a few
megabytes. If the limits come close, publish the same site tree to object
storage behind the same `apt.linbox.in` name. Clients don't need to change
anything, because trust comes from the signature, not the host.
