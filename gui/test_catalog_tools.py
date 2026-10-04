#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import catalog_tools as tools


def sample() -> dict:
    return {
        "test_rule": tools.VM_RULE,
        "vendors": [
            {
                "vendor": "NVIDIA",
                "open_source": "nouveau",
                "branches": [
                    {
                        "branch": "470.xx",
                        "cards": ["Kepler", "GeForce GTX 600"],
                        "source": "https://www.nvidia.com/en-us/drivers/unix/",
                    }
                ],
            }
        ],
    }


class CatalogToolTests(unittest.TestCase):
    def test_check_passes_a_complete_catalog(self):
        ok, errors = tools.check_catalog(sample())
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_check_fails_without_the_vm_rule(self):
        data = sample()
        data["test_rule"] = "install anywhere"
        ok, errors = tools.check_catalog(data)
        self.assertFalse(ok)
        self.assertIn("missing VM-only rule", errors)

    def test_search_finds_a_card(self):
        found = tools.search_rows(tools.rows(sample()), "gtx 600")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["branch"], "470.xx")
        self.assertEqual(found[0]["open_source"], "nouveau")

    def test_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(sample()), encoding="utf-8")
            loaded = tools.load_catalog(path)
        self.assertEqual(loaded["vendors"][0]["vendor"], "NVIDIA")


if __name__ == "__main__":
    unittest.main()
