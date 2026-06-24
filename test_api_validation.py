import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app


class ApiValidationTests(unittest.TestCase):
    @patch("api.run_agent")
    def test_chat_returns_422_and_does_not_call_agent_for_empty_question(
        self,
        mocked_run_agent
    ):
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"question": ""}
        )



        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        first_error = detail[0]

        self.assertEqual(
            first_error["loc"],
            ["body", "question"]
        )
        mocked_run_agent.assert_not_called()


if __name__ == "__main__":
    unittest.main()