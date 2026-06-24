import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app

from agent_errors import AgentServiceUnavailableError


class ApiLoggingTests(unittest.TestCase):
    @patch("api.run_agent")
    def test_chat_logs_success_without_question_content(
        self,
        mocked_run_agent
    ):
        mocked_run_agent.return_value = {
            "answer": "RAG 是检索增强生成。",
            "sources": [2],
            "step_count": 2
        }

        client = TestClient(app)

        with self.assertLogs(
            "personal_knowledge_agent.api",
            level="INFO"
        ) as captured_logs:
            response = client.post(
                "/chat",
                json={"question": "这是不应写入日志的问题"}
            )

        self.assertEqual(response.status_code, 200)

        log_text = "\n".join(captured_logs.output)

        self.assertIn(
            "event=chat_request_completed",
            log_text
        )
        self.assertIn("status_code=200", log_text)
        self.assertIn("outcome=success", log_text)

        self.assertNotIn(
            "这是不应写入日志的问题",
            log_text
        )
    
    @patch("api.run_agent")
    def test_chat_logs_validation_failure_without_calling_agent(
        self,
        mocked_run_agent
    ):
        client = TestClient(app)

        with self.assertLogs(
            "personal_knowledge_agent.api",
            level="INFO"
        ) as captured_logs:
            response = client.post(
                "/chat",
                json={"question": ""}
            )

        self.assertEqual(response.status_code, 422)
        mocked_run_agent.assert_not_called()

        log_text = "\n".join(captured_logs.output)

        self.assertIn("status_code=422", log_text)
        self.assertIn(
            "outcome=request_validation_failed",
            log_text
        )

        

    @patch("api.run_agent")
    def test_chat_logs_service_unavailable(
        self,
        mocked_run_agent
    ):
        mocked_run_agent.side_effect = AgentServiceUnavailableError(
            "模型服务暂时不可用"
        )

        client = TestClient(app)

        with self.assertLogs(
            "personal_knowledge_agent.api",
            level="INFO"
        ) as captured_logs:
            response = client.post(
                "/chat",
                json={"question": "什么是 RAG？"}
            )

        self.assertEqual(response.status_code, 503)

        log_text = "\n".join(captured_logs.output)

        self.assertIn("status_code=503", log_text)
        self.assertIn(
            "outcome=agent_service_unavailable",
            log_text
        )


if __name__ == "__main__":
    unittest.main()