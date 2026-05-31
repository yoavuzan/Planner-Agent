import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nodes.executor import executor_node
from langchain_core.messages import HumanMessage, AIMessage

class TestExecutorNode(unittest.TestCase):
    def test_executor_node_basic(self):
        # Mock model
        mock_model = MagicMock()
        mock_response = AIMessage(content="I have written the file.")
        mock_model.invoke.return_value = mock_response

        # State
        state = {
            "plan": ["Create file.py"],
            "completed_tasks": [],
            "messages": [HumanMessage(content="Test request")]
        }

        # Run node
        result = executor_node(state, mock_model)

        # Assertions
        self.assertEqual(result["current_task"], "Create file.py")
        self.assertEqual(result["messages"][0].content, "I have written the file.")
        mock_model.invoke.assert_called_once()

if __name__ == '__main__':
    unittest.main()
