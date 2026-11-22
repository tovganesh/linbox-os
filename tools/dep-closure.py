#!/usr/bin/env python3
"""Approximate the dependency closure of Debian packages from a Packages index.

Used to review a package selection before building, e.g. "does this set pull
in Xorg?". It is an approximation of apt: for each alternative group it picks
the first alternative that exists (real or virtual), and it ignores versions.
The authoritative check is the build-time hook that inspects the real chroot.

Usage:
  dep-closure.py PACKAGES_FILE [--recommends] [--why REGEX] pkg [pkg ...]

A package suffixed with "-" is excluded (apt's "pkg-" syntax).
"""
import argparse
import re
import sys
from collections import deque


def parse_packages(path):
    pkgs, provides = {}, {}
    with open(path, encoding="utf-8", errors="replace") as f:
        stanza = {}
        key = None
        for line in f:
            if line == "\n":
                if "Package" in stanza:
                    name = stanza["Package"]
                    pkgs[name] = stanza
                    for prov in split_rel(stanza.get("Provides", "")):
                        provides.setdefault(prov[0], []).append(name)
                stanza, key = {}, None
                continue
            if line[0] in " \t" and key:
                stanza[key] += " " + line.strip()
            else:
                key, _, val = line.partition(":")
                stanza[key] = val.strip()
    return pkgs, provides


def split_rel(field):
    """'a (>= 1) | b, c' -> [['a', 'b'], ['c']] ; also used for Provides."""
    groups = []
    for grp in field.split(","):
        grp = grp.strip()
        if not grp:
            continue
        alts = [re.sub(r"\s*[\(\[<].*$", "", a.strip()).split(":")[0] for a in grp.split("|")]
        groups.append([a for a in alts if a])
    return groups


def resolve(name, pkgs, provides, excluded):
    if name in excluded:
        return None
    if name in pkgs:
        return name
    for real in provides.get(name, []):
        if real not in excluded:
            return real
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("packages_file")
    ap.add_argument("--recommends", action="store_true", help="follow Recommends too (apt default)")
    ap.add_argument("--why", help="regex: print the dependency path to matching packages")
    ap.add_argument("roots", nargs="+")
    args = ap.parse_args()

    pkgs, provides = parse_packages(args.packages_file)
    excluded = {r[:-1] for r in args.roots if r.endswith("-")}
    roots = [r for r in args.roots if not r.endswith("-")]

    parent = {}
    queue = deque()
    for r in roots:
        real = resolve(r, pkgs, provides, excluded)
        if real is None:
            print(f"E: root package not found: {r}", file=sys.stderr)
            return 2
        parent.setdefault(real, None)
        queue.append(real)

    fields = ["Pre-Depends", "Depends"] + (["Recommends"] if args.recommends else [])
    while queue:
        cur = queue.popleft()
        for fld in fields:
            for alts in split_rel(pkgs[cur].get(fld, "")):
                if any(a in parent for a in alts):
                    continue  # group already satisfied
                for a in alts:
                    real = resolve(a, pkgs, provides, excluded)
                    if real:
                        if real not in parent:
                            parent[real] = cur
                            queue.append(real)
                        break

    if args.why:
        rx = re.compile(args.why)
        hits = sorted(p for p in parent if rx.search(p))
        for h in hits:
            path, p = [], h
            while p is not None:
                path.append(p)
                p = parent[p]
            print(" <- ".join(path))
        print(f"{len(hits)} matching of {len(parent)} packages in closure")
        return 1 if hits else 0
    for p in sorted(parent):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
