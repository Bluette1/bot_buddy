import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import bot

@pytest.fixture
def mock_ctx(mocker):
    ctx = mocker.Mock()
    ctx.send = mocker.AsyncMock()
    ctx.author.id = 123456789
    return ctx

@pytest.fixture
def mock_conversations_collection(mocker):
    return mocker.patch('bot.conversations_collection')

@pytest.fixture
def mock_quotes_collection(mocker):
    return mocker.patch('bot.quotes_collection')


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
async def test_inspire_command(mock_ctx, mock_quotes_collection):
    # Setup a mock quote
    mock_quotes_collection.aggregate.return_value = iter([{"text": "Stay positive.", "author": "Anonymous"}])

    # Call the inspire command
    await bot.get_command("inspire")(mock_ctx)

    # Check if the correct message was sent
    mock_ctx.send.assert_called_once_with('"Stay positive." - Anonymous')

@pytest.mark.asyncio
async def test_inspire_command_no_quotes(mock_ctx, mock_quotes_collection):
    # Setup no quotes
    mock_quotes_collection.aggregate.return_value = iter([])

    # Call the inspire command
    await bot.get_command("inspire")(mock_ctx)

    # Check if the fallback message was sent
    mock_ctx.send.assert_called_once_with("Sorry, I couldn't find any quotes.")

@pytest.mark.asyncio
async def test_on_member_join(mocker):
    # Create mock member and channel
    mock_member = mocker.Mock()
    mock_member.mention = '@new_member'
    mock_member.name = 'new_member'
    mock_member.send = mocker.AsyncMock()  # Ensure this is an async mock

    mock_channel = mocker.Mock()
    mock_channel.send = mocker.AsyncMock()

    # Patch bot.get_channel
    with patch('bot.bot.get_channel', return_value=mock_channel):
        await bot.on_member_join(mock_member)

    # Check if welcome messages were sent
    mock_channel.send.assert_called_once_with("Welcome to the server, @new_member! 🎉 We're glad to have you here!")
    mock_member.send.assert_called_once_with("Hi new_member, welcome to our Discord server! Feel free to ask if you need any help.")

@pytest.mark.asyncio
async def test_ask_command(mock_ctx, mock_conversations_collection):
    # Call the ask command
    await bot.get_command("ask")(mock_ctx)

    # Check if the correct message was sent
    mock_ctx.send.assert_called_once_with("Fire away!")

    # Check that the conversation was initialized in the database
    mock_conversations_collection.update_one.assert_called_once_with(
        {"user_id": mock_ctx.author.id}, {"$set": {"messages": []}}, upsert=True
    )

