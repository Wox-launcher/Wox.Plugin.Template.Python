import unittest
from types import SimpleNamespace

from wox_plugin import Context, QueryResponse

from src.main import MyPlugin


class TestMyPlugin(unittest.IsolatedAsyncioTestCase):
    async def test_query_returns_result_and_action_data(self):
        response = await MyPlugin().query(Context(), SimpleNamespace(search="Hello"))
        self.assertIsInstance(response, QueryResponse)
        self.assertEqual(response.results[0].title, "you typed hello")
        self.assertEqual(response.results[0].actions[0].context_data, {"search_term": "hello"})


if __name__ == "__main__":
    unittest.main()
