# Linbox archive public keys

Public keys only. `tools/make-archive-key` writes a new key here as
`linbox-archive-<year>.asc`. During a rotation, both the old and new keys
stay here until every supported release has the new one. Never put secret
keys in this directory. See [docs/apt-repository.md](../../../docs/apt-repository.md).
