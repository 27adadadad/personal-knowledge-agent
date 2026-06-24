import os
import unittest
from unittest.mock import patch

import requests
from langchain_core.messages import HumanMessage

from agent_errors import AgentServiceUnavailableError
from agent_model import model_node


class AgentModelErrorTests(unittest.TestCase):
    @patch.dict(
        os.environ,
        {"DASHSCOPE_API_KEY": "test-key"}
    )
    @patch("agent_model.ask_qwen_with_tools")
    def test_model_node_raises_service_error_when_qwen_request_fails(
        self, 
        mocked_ask_qwen
    ):
        mocked_ask_qwen.side_effect = requests.RequestException(
            "网络连接失败"
        )

        state = {
            "question": "什么是 RAG？",
            "messages": [
                HumanMessage(content="什么是 RAG？")
            ],
            "answer": "",
            "step_count": 0
        }

        with self.assertRaises(AgentServiceUnavailableError):
            model_node(state)

if __name__ == "__main__":
    unittest.main()
