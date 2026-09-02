#!/usr/bin/env python3
"""Build index.json from the blueprints/ and skills/ trees.

The index is what a consumer parses to learn what this catalog holds: every
blueprint and skill, its current version, a one-line summary for a list row,
and the sha256 of each of its files.

Deliberately deterministic — sorted keys, no timestamp, LF endings, trailing
newline. Rebuilding an unchanged tree produces byte-identical output, so "does
this index match these files?" is answerable by rebuilding and diffing. That
property is worth more than an embedded build date.

The index is NOT committed. It is generated at release time and uploaded as a
release asset. A committed index silently drifts from the files it describes; a
generated one cannot.

Signing: not yet, and on purpose. While this catalog is prose, a tampered
blueprint's worst case is a proposal a person rejects item by item, having seen
each one literally. Hashes are here from the first release because they are
cheap and drive update detection — and because they are what a signature will
later cover. See docs/blueprints.md §7.1 in the monorepo; signing becomes
mandatory before the first executable ships.

Usage:
    scripts/build-index.py <catalog_version> [output_path]
"""

import hashlib
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml (or apt install python3-yaml)")

INDEX_SCHEMA = 1
SUMMARY_MAX = 240

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (tree, manifest filename, id field, extra published files)
KINDS = (
    ("blueprints", "blueprint.yaml", "blueprint", ()),
    ("skills", "skill.yaml", "skill", ("SKILL.md",)),
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def discover(tree, manifest_name):
    """Yield (slug, directory) for every <tree>/<namespace>/<name>/."""
    root = os.path.join(REPO_ROOT, tree)
    if not os.path.isdir(root):
        return
    for namespace in sorted(os.listdir(root)):
        ns_dir = os.path.join(root, namespace)
        if not os.path.isdir(ns_dir):
            continue
        for name in sorted(os.listdir(ns_dir)):
            d = os.path.join(ns_dir, name)
            if os.path.isfile(os.path.join(d, manifest_name)):
                yield "%s/%s" % (namespace, name), d


def clip(text):
    text = " ".join((text or "").split())
    if len(text) <= SUMMARY_MAX:
        return text
    return text[:SUMMARY_MAX].rsplit(" ", 1)[0] + "…"


def require(doc, field, slug, path):
    value = doc.get(field)
    if value in (None, ""):
        sys.exit("%s (%s): missing required field %r" % (slug, path, field))
    return value


def check_blueprint(slug, doc, known_skills):
    """Validate a blueprint far enough that publishing it can't ship a dud."""
    for item in doc.get("items") or []:
        if not isinstance(item, dict):
            sys.exit("%s: an item is not a mapping" % slug)
        for field in ("op", "primitive"):
            if not item.get(field):
                sys.exit("%s: an item is missing %r" % (slug, field))

    # Every ${handle.id} must name a handle this plan actually declares, and
    # every handle in depends_on likewise. A dangling reference fails at apply,
    # halfway through building someone's household — much better to fail here.
    handles = {i["handle"] for i in (doc.get("items") or [])
               if isinstance(i, dict) and i.get("handle")}
    blob = json.dumps(doc.get("items") or [])
    for ref in _tokens(blob, "${", "}"):
        name = ref.split(".", 1)[0]
        if name not in handles:
            sys.exit("%s: ${%s} references a handle no item declares" % (slug, ref))
    for item in doc.get("items") or []:
        for dep in item.get("depends_on") or []:
            if dep not in handles:
                sys.exit("%s: depends_on %r names a handle no item declares" % (slug, dep))

    # Same for @{alias}: it must be a declared requirement or an implicit
    # binding, or materialization has nothing to bind it to.
    implicit = {"harness", "agent_home"}
    aliases = {r.get("alias") for r in (doc.get("requires") or []) if isinstance(r, dict)}
    for ref in _tokens(blob, "@{", "}"):
        name = ref.split(":", 1)[0]
        if name not in aliases and name not in implicit and not ref.startswith("model:"):
            sys.exit("%s: @{%s} is neither a declared requirement nor an implicit binding"
                     % (slug, ref))

    for ref in doc.get("skills") or []:
        if isinstance(ref, dict) and ref.get("skill") not in known_skills:
            sys.exit("%s: references skill %r, which is not in this catalog"
                     % (slug, ref.get("skill")))


def _tokens(blob, open_tok, close_tok):
    out, i = [], 0
    while True:
        start = blob.find(open_tok, i)
        if start < 0:
            return out
        end = blob.find(close_tok, start)
        if end < 0:
            return out
        out.append(blob[start + len(open_tok):end])
        i = end + 1


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    catalog_version = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO_ROOT, "index.json")

    index = {"index_schema": INDEX_SCHEMA, "catalog_version": catalog_version}
    docs = {}

    for tree, manifest_name, id_field, extra in KINDS:
        entries = {}
        for slug, directory in discover(tree, manifest_name):
            manifest_path = os.path.join(directory, manifest_name)
            with open(manifest_path) as f:
                doc = yaml.safe_load(f) or {}
            declared = require(doc, id_field, slug, manifest_path)
            if declared != slug:
                sys.exit("%s: %s field says %r but it lives at %s/"
                         % (slug, id_field, declared, slug))

            files = {}
            for filename in (manifest_name,) + extra:
                path = os.path.join(directory, filename)
                if os.path.isfile(path):
                    files[filename] = "sha256:" + sha256_file(path)
            content = doc.get("content")
            if content and content not in files:
                path = os.path.join(directory, content)
                if not os.path.isfile(path):
                    sys.exit("%s: content: %r does not exist" % (slug, content))
                files[content] = "sha256:" + sha256_file(path)

            entries[slug] = {
                "version": str(require(doc, "version", slug, manifest_path)),
                "display_name": require(doc, "display_name", slug, manifest_path),
                "summary": clip(require(doc, "summary", slug, manifest_path)),
                "tags": sorted(doc.get("tags") or []),
                "files": files,
            }
            if doc.get("min_relay_version"):
                entries[slug]["min_relay_version"] = str(doc["min_relay_version"])
            docs[slug] = doc
        index[tree] = entries

    known_skills = set(index.get("skills", {}))
    for slug in sorted(index.get("blueprints", {})):
        check_blueprint(slug, docs[slug], known_skills)

    with open(out_path, "w") as f:
        json.dump(index, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    print("wrote %s — %d blueprints, %d skills"
          % (out_path, len(index.get("blueprints", {})), len(index.get("skills", {}))))


if __name__ == "__main__":
    main()
