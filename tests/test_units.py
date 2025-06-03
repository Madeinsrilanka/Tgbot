import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from your_bot_file import SystemMonitor, MovieBotUtils

class TestSystemMonitor(unittest.TestCase):
    def test_get_system_ram(self):
        ram = SystemMonitor.get_system_ram()
        self.assertIsInstance(ram, str)
        self.assertIn("GB", ram)

class TestMovieBotUtils(unittest.TestCase):
    @patch('your_bot_file.requests.get')
    def test_fetch_api_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = MovieBotUtils.fetch_api("/test", {})
        self.assertEqual(result, {"result": "success"})
