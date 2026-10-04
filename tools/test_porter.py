#!/usr/bin/env python3
import unittest

import porter


class PorterTests(unittest.TestCase):
    def test_greets_a_new_programmer(self):
        self.assertTrue(porter.should_greet("newdev", 0))
        text = porter.welcome("newdev")
        self.assertIn("Welcome, newdev.", text)
        self.assertIn("I will show you around.", text)
        self.assertIn("gui/driver_gui.py", text)
        self.assertIn("gui_bug_report.yml", text)
        self.assertIn("GNU GPL version 3", text)
        self.assertIn("drivers/old-gpu-catalog.json", text)
        self.assertIn("scripts/check-catalog.py", text)
        self.assertIn("discussions/3", text)
        self.assertIn("quarantine", text)
        self.assertIn("Linux virtual machine", text)
        self.assertIn("Do not run this on a main machine or bare metal.", text)

    def test_skips_owner_bot_and_return_visits(self):
        self.assertFalse(porter.should_greet("anyones2019-cloud", 0))
        self.assertFalse(porter.should_greet("github-actions[bot]", 0))
        self.assertFalse(porter.should_greet("newdev", 2))


if __name__ == "__main__":
    unittest.main()
