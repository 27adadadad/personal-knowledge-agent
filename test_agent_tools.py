import unittest 
from unittest.mock import patch

import requests

from agent_errors import AgentServiceUnavailableError
from agent_tools import search_knowledge

class AgentTooolErrorTests(unittest.TestCase):
    def test_search_knowledge_raise_service_error_when_embedding_fails(
            self
    ):
        with patch(
            "agent_tools.load_knowledge",
            return_value=[]
        ):
            with patch(
                "agent_tools.get_or_build_vector_index",
                side_effect=requests.RequestException(
                    "Embedding 服务连接失败"
                )
            ):
                with self.assertRaises(
                    AgentServiceUnavailableError
            ):
                    search_knowledge.invoke(
                        {"query": "什么是 RAG？"}
                    )

if __name__ == "__main__":
    unittest.main()