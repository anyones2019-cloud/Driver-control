#!/usr/bin/env python3
import unittest

import moderate_discussion as bot


class ModeratorTests(unittest.TestCase):
    def test_sorts_a_bug(self):
        text = bot.reply("Install crash", "The catalog check failed", "volunteer")
        self.assertIn("Sorted as: bug.", text)
        self.assertIn("does not close or delete", text)

    def test_sorts_an_unsafe_request(self):
        text = bot.reply("Try it", "I will run this on my main machine", "guest")
        self.assertIn("Sorted as: unsafe request.", text)
        self.assertIn("virtual machine", text)

    def test_swear_gets_a_finger_wag(self):
        text = bot.reply("Tone", "what the " + "fuck is this", "guest")
        self.assertIn("👆 No no.", text)

    def test_clean_chat_has_no_finger_wag(self):
        text = bot.reply("Idea", "A quiet question about Fedora", "guest")
        self.assertNotIn("👆", text)
        text = bot.reply("Note", "Just an idea", "anyones2019-cloud")
        self.assertIn("does not pick on them", text)
        self.assertNotIn("Sorted as: unsafe", text)


if __name__ == "__main__":
    unittest.main()
