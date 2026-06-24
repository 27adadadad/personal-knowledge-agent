import unittest

from agent_errors import AgentServiceUnavailableError


class AgentErrorTests(unittest.TestCase):
    def test_service_unavailable_error_can_be_raised(self):
        with self.assertRaises(AgentServiceUnavailableError):
            raise AgentServiceUnavailableError("模型服务暂时不可用")


if __name__ == "__main__":
    unittest.main()