# # tests/test_bot.py
# from bot import bot  # Adjust based on your structure
# import os
# import pytest
# from discord.ext import commands
# from dotenv import load_dotenv
# from unittest.mock import AsyncMock, MagicMock

# load_dotenv()

# DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# MONGODB_URI = os.getenv("MONGODB_URI")


# def test_load_environment_variables():
#     assert DISCORD_TOKEN is not None, "DISCORD_TOKEN should not be None"
#     assert MONGODB_URI is not None, "MONGODB_URI should not be None"
#     assert "Pong! Latency is" in mock_ctx.send.call_args[0][0]


# @pytest.mark.asyncio
# async def test_ping_command(mocker):
#     # Create a mock context
#     mock_ctx = mocker.Mock()
#     mock_ctx.send = mocker.AsyncMock()

#     # Mock the latency attribute by creating a mock bot
#     mock_bot = mocker.patch("bot.bot", autospec=True)
#     mock_bot.latency = 0.123  # Set a realistic latency value for testing

#     # Call the ping command
#     await bot.get_command("ping")(mock_ctx)

#     # Assert the send method was called with the correct message
#     mock_ctx.send.assert_called_once()
#     assert "Pong! Latency is 123ms" in mock_ctx.send.call_args[0][0]


# @pytest.mark.asyncio
# async def test_hello_command(mocker):
#     # Create a mock context
#     mock_ctx = mocker.Mock()
#     mock_ctx.send = mocker.AsyncMock()

#     # Call the hello command
#     await bot.get_command("hello")(mock_ctx)

#     # Assert the send method was called with the correct message
#     mock_ctx.send.assert_called_once()
#     assert "Hello!" in mock_ctx.send.call_args[0][0]


# @pytest.mark.asyncio
# async def test_ask_command(mocker):
#     # Create a mock context
#     mock_ctx = mocker.Mock()
#     mock_ctx.send = mocker.AsyncMock()  # Mock the send method to be async

#     # Call the ask command
#     await bot.get_command("ask")(mock_ctx)

#     # Assert that the correct message was sent
#     mock_ctx.send.assert_called_once_with("Fire away!")


# @pytest.mark.asyncio
# async def test_ask_command(mocker):
#     # Create a mock context
#     mock_ctx = mocker.Mock()
#     mock_ctx.send = mocker.AsyncMock()  # Mock the send method to be async

#     # Call the ask command
#     await bot.get_command("ask")(mock_ctx)

#     # Assert that the correct message was sent
#     mock_ctx.send.assert_called_once_with("Fire away!")


# @pytest.mark.asyncio
# async def test_ask_command(mocker):
#     # Create a mock context
#     mock_ctx = MagicMock()

#     # Create a mock author with an ID
#     mock_ctx.author.id = 123456789  # Use a valid user ID for testing
#     mock_ctx.send = AsyncMock()  # Mock the send method to be async

#     # Mock the MongoDB collection to prevent actual database calls
#     mock_collection = mocker.patch('bot.conversations_collection')

#     # Call the ask command
#     await bot.get_command("ask")(mock_ctx)

#     # Assert that the correct message was sent
#     mock_ctx.send.assert_called_once_with("Fire awqay!")

#     # Check that the update_one was called to initialize conversation history
#     mock_collection.update_one.assert_called_once_with(
#         {"user_id": mock_ctx.author.id}, {"$set": {"messages": []}}, upsert=True
#     )
# tests/test_bot.py
from bot import bot  # Adjust based on your structure
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_ctx(mocker):
    ctx = mocker.Mock()
    ctx.send = mocker.AsyncMock()
    ctx.author.id = 123456789  # Use a valid user ID for testing
    return ctx

@pytest.fixture
def mock_collection(mocker):
    return mocker.patch('bot.conversations_collection')

def test_load_environment_variables():
    assert os.getenv("DISCORD_BOT_TOKEN") is not None, "DISCORD_TOKEN should not be None"
    assert os.getenv("MONGODB_URI") is not None, "MONGODB_URI should not be None"

@pytest.mark.asyncio
async def test_ping_command(mock_ctx, mocker):
    # Mock the latency attribute by creating a mock bot
    mock_bot = mocker.patch("bot.bot", autospec=True)
    mock_bot.latency = 0.123  # Set a realistic latency value for testing

    # Call the ping command
    await bot.get_command("ping")(mock_ctx)

    # Assert the send method was called with the correct message
    mock_ctx.send.assert_called_once()
    assert "Pong! Latency is 123ms" in mock_ctx.send.call_args[0][0]

@pytest.mark.asyncio
async def test_hello_command(mock_ctx):
    # Call the hello command
    await bot.get_command("hello")(mock_ctx)

    # Assert the send method was called with the correct message
    mock_ctx.send.assert_called_once_with("Hello!")

@pytest.mark.asyncio
async def test_ask_command(mock_ctx, mock_collection):
    # Call the ask command
    await bot.get_command("ask")(mock_ctx)

    # Assert that the correct message was sent
    mock_ctx.send.assert_called_once_with("Fire away!")

    # Check that the update_one was called to initialize conversation history
    mock_collection.update_one.assert_called_once_with(
        {"user_id": mock_ctx.author.id}, {"$set": {"messages": []}}, upsert=True
    )