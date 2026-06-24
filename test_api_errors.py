import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agent_errors import AgentServiceUnavailableError
from api import app


class ApiErrorTests(unittest.TestCase):
    @patch("api.run_agent")
    def test_chat_returns_503_when_agent_service_is_unavailable(
        self,
        mocked_run_agent
    ):
        mocked_run_agent.side_effect = AgentServiceUnavailableError(
            "模型服务暂时不可用"
        )

        client = TestClient(
            app,
            raise_server_exceptions=False
        )

        response = client.post(
            "/chat",
            json={"question": "什么是 RAG？"}
        )

        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()