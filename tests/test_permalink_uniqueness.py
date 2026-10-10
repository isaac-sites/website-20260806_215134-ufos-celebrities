"""Falsifier for the ufos-and-celebrities-846269 permalink collision cure.

Before the cure, two truncated permalinks were claimed by ten level-3
``*_index.md`` documents (8+2 colliding), shadowing eight indexes. The cure
keeps the live winner at each shared route and gives every shadowed index a
unique ``-<index title>`` suffixed permalink.
"""
import io
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
PERMALINK = re.compile(r"^permalink:\s*[\"']?([^\s\"'#]+)[\"']?\s*$", re.M)


def page_permalinks():
    out = {}
    for p in PAGES.glob("*.md"):
        m = FRONT_MATTER.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        pm = PERMALINK.search(m.group(1))
        if pm:
            out[p.name] = pm.group(1)
    return out


SHARED_SLUGS = {
    "/ufos-and-celebrities-846269-celebrity/",
    "/ufos-and-celebrities-846269-phoenix/",
}

EXPECTED_CURED = {
    "/ufos-and-celebrities-846269-celebrity-official-actions/",
    "/ufos-and-celebrities-846269-celebrity-pilot-witnesses/",
    "/ufos-and-celebrities-846269-celebrity-fame-vs-evidence/",
    "/ufos-and-celebrities-846269-celebrity-documentaries/",
    "/ufos-and-celebrities-846269-celebrity-media-amplification/",
    "/ufos-and-celebrities-846269-celebrity-eyewitness-memory/",
    "/ufos-and-celebrities-846269-celebrity-reporting-stigma/",
    "/ufos-and-celebrities-846269-phoenix-flare-debate/",
}


class TestPermalinkUniqueness(unittest.TestCase):
    def test_all_permalinks_unique(self):
        pls = page_permalinks()
        counts = Counter(pls.values())
        dups = {k: v for k, v in counts.items() if v > 1}
        owners = {k: sorted(n for n, v in pls.items() if v == k) for k in dups}
        self.assertEqual({}, owners)

    def test_shared_family_slugs_claimed_by_one_document(self):
        pls = page_permalinks()
        for slug in SHARED_SLUGS:
            owners = sorted(n for n, v in pls.items() if v == slug)
            self.assertEqual(1, len(owners), f"{slug} claimed by {owners}")

    def test_expected_cured_index_routes_exist(self):
        pls = set(page_permalinks().values())
        self.assertEqual(set(), EXPECTED_CURED - pls)

    def test_manifest_canonical_urls_for_cured_indexes(self):
        # Pin only the eight cured entries; the manifest carries pre-existing
        # drift elsewhere and a uniform https://None/None/ host prefix.
        manifest = json.loads(io.open(ROOT / "phoenix-manifest.json", encoding="utf-8").read())
        cured = {k[:-3]: v for k, v in {
            "ufos_and_celebrities_846269_celebrity_advocacy_o_b06026_index.md": "/ufos-and-celebrities-846269-celebrity-official-actions/",
            "ufos_and_celebrities_846269_celebrity_pilot_ufo_a48907_index.md": "/ufos-and-celebrities-846269-celebrity-pilot-witnesses/",
            "ufos_and_celebrities_846269_celebrity_status_vs_fc4dbb_index.md": "/ufos-and-celebrities-846269-celebrity-fame-vs-evidence/",
            "ufos_and_celebrities_846269_celebrity_ufo_docume_bdf581_index.md": "/ufos-and-celebrities-846269-celebrity-documentaries/",
            "ufos_and_celebrities_846269_celebrity_ufo_media_cef9da_index.md": "/ufos-and-celebrities-846269-celebrity-media-amplification/",
            "ufos_and_celebrities_846269_celebrity_ufo_memory_f7cd1d_index.md": "/ufos-and-celebrities-846269-celebrity-eyewitness-memory/",
            "ufos_and_celebrities_846269_celebrity_ufo_report_4341fd_index.md": "/ufos-and-celebrities-846269-celebrity-reporting-stigma/",
            "ufos_and_celebrities_846269_phoenix_lights_flare_fb02f3_index.md": "/ufos-and-celebrities-846269-phoenix-flare-debate/",
        }.items()}
        bad = []
        for page in manifest.get("pages", []):
            lid = page.get("logical_id")
            if lid in cured:
                route = "/" + (page.get("canonical_url") or "").split("/", 3)[-1].split("/", 1)[-1]
                if route != cured[lid]:
                    bad.append((lid, route, cured[lid]))
        self.assertEqual([], bad)

    def test_index_bodies_link_only_existing_routes(self):
        existing = set(page_permalinks().values())
        dangling = []
        for p in PAGES.glob("*_index.md"):
            for m in re.finditer(r"\{\{\s*'(/[^']*?)'\s*\|\s*relative_url", p.read_text(encoding="utf-8", errors="replace")):
                if m.group(1) not in existing:
                    dangling.append((p.name, m.group(1)))
        self.assertEqual([], dangling)


if __name__ == "__main__":
    unittest.main()
