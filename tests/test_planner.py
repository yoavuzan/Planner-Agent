
import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nodes.planner import planner_node
from langchain_core.messages import HumanMessage

class TestPlannerNode(unittest.TestCase):
    def test_planner_node_basic(self):
        # Mock model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "['Task 1', 'Task 2']"
        mock_model.invoke.return_value = mock_response

        # State
        state = {
            "messages": [HumanMessage(content="Test request")]
        }

        # Run node
        result = planner_node(state, mock_model)

        # Assertions
        self.assertEqual(result["plan"], ["Task 1", "Task 2"])
        self.assertEqual(result["completed_tasks"], [])
        mock_model.invoke.assert_called_once()

if __name__ == '__main__':
    unittest.main()
