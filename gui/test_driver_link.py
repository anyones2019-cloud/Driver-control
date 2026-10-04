#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import catalog_tools as tools

ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "scripts" / "driver_link.py"


class DriverLinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DRIVER_CONTROL_DATA"] = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_tools_selection_is_what_the_driver_reads(self):
        item = {
            "vendor": "NVIDIA",
            "branch": "470.xx",
            "cards": "Kepler",
            "open_source": "nouveau",
            "source": "https://www.nvidia.com/en-us/drivers/unix/",
        }
        tools.write_selection(item)
        result = subprocess.run([sys.executable, str(LINK)], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn(item["open_source"], result.stdout)
        self.assertIn("does not install a driver", result.stdout)
        self.assertFalse(tools.read_selection()["install"])

    def test_driver_refuses_to_install(self):
        tools.write_selection({"vendor": "NVIDIA", "branch": "470.xx", "cards": "Kepler", "open_source": "nouveau", "source": "https://example.test"})
        result = subprocess.run([sys.executable, str(LINK), "--install"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Refusing to install", result.stdout)


if __name__ == "__main__":
    unittest.main()
