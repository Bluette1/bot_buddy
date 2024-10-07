# tests/test_commands.py
import pytest
from bot import bot, ping, on_message  # Adjust according to your file structure
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_ping_command(mocker):
    mock_ctx = Mock()
    await ping(mock_ctx)
    mock_ctx.send.assert_called_with(f"Pong! Latency is {round(bot.latency * 1000)}ms")

# Additional tests can go here
