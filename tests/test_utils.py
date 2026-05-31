import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nodes.utils import parse_llm_list

class TestUtils(unittest.TestCase):
    def test_parse_llm_list_clean(self):
        content = "['Task 1', 'Task 2']"
        expected = ["Task 1", "Task 2"]
        self.assertEqual(parse_llm_list(content), expected)

    def test_parse_llm_list_markdown(self):
        content = "```python\n['Task 1', 'Task 2']\n```"
        expected = ["Task 1", "Task 2"]
        self.assertEqual(parse_llm_list(content), expected)

    def test_parse_llm_list_with_text(self):
        content = "Here is the list: ['Task 1', 'Task 2'] and some more text."
        expected = ["Task 1", "Task 2"]
        self.assertEqual(parse_llm_list(content), expected)

    def test_parse_llm_list_fallback(self):
        content = "1. Task 1\n2. Task 2"
        expected = ["Task 1", "Task 2"]
        self.assertEqual(parse_llm_list(content), expected)

if __name__ == '__main__':
    unittest.main()
