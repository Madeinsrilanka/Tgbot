import unittest
from unittest.mock import AsyncMock, patch
from your_bot_file import start, help_command

class TestBotCommands(unittest.IsolatedAsyncioTestCase):
    async def test_start_command(self):
        update = AsyncMock()
        context = AsyncMock()
        
        await start(update, context)
        
        update.message.reply_text.assert_called_once()
        self.assertIn("Welcome", update.message.reply_text.call_args[0][0])

    async def test_help_command(self):
        update = AsyncMock()
        context = AsyncMock()
        
        await help_command(update, context)
        
        update.message.reply_text.assert_called_once()
        self.assertIn("Help Menu", update.message.reply_text.call_args[0][0])
