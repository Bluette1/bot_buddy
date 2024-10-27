import os
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from discord.ext.commands import Context, Bot, MissingPermissions
from discord import Intents, Member, TextChannel
from bot import (
    set_welcome_message,
    view_welcome_message,
    view_newyear_message,
    set_newyear_message,
    on_member_join,
    ping,
    hello,
    ask,
    inspire,
    set_welcome_message_error,
    set_newyear_message_error,
    check_new_year
)


@pytest.fixture
def mock_conversations_collection(mocker):
    return mocker.patch('bot.conversations_collection')


@pytest.fixture
def mock_quotes_collection(mocker):
    return mocker.patch('bot.quotes_collection')


@pytest.fixture
def mock_messages_collection(mocker):
    return mocker.patch('bot.messages_collection')


@pytest.fixture
def mock_bot():
    intents = Intents.default()
    bot = Bot(command_prefix="!", intents=intents)
    return bot

@pytest.fixture
def mock_ctx(mocker, mock_bot):
    ctx = mocker.Mock(spec=Context)
    ctx.bot = mock_bot
    ctx.send = AsyncMock()
    ctx.author = mocker.Mock()
    ctx.author.guild_permissions = mocker.Mock()
    ctx.guild = mocker.Mock()
    ctx.guild.id = 987654321
    ctx.message = mocker.Mock()
    return ctx


def test_load_environment_variables():
    assert os.getenv("DISCORD_BOT_TOKEN") is not None, "DISCORD_TOKEN should not be None"
    assert os.getenv("MONGODB_URI") is not None, "MONGODB_URI should not be None"

@pytest.mark.asyncio
async def test_set_welcome_message_without_permissions(mock_ctx):
    mock_ctx.author.guild_permissions.administrator = False
    
    error = MissingPermissions(['administrator'])
    
    await set_welcome_message_error(mock_ctx, error)
    
    mock_ctx.send.assert_called_once_with("You do not have the correct permissions to use this command.")

@pytest.mark.asyncio
async def test_set_welcome_message_with_permissions(mock_ctx):
    mock_ctx.author.guild_permissions.administrator = True
    
    with patch('bot.messages_collection') as mock_messages_collection:
        await set_welcome_message(mock_ctx, message="Welcome!")
        
        mock_messages_collection.update_one.assert_called_once_with(
            {"_id": f"welcome_message_{mock_ctx.guild.id}"},
            {"$set": {"message": "Welcome!"}},
            upsert=True
        )
        mock_ctx.send.assert_called_once_with("Welcome message updated to: Welcome!")


@pytest.mark.asyncio
async def test_view_welcome_message_with_existing_message(mock_ctx):
    with patch('bot.messages_collection') as mock_messages_collection:
        mock_messages_collection.find_one.return_value = {"message": "Custom Welcome!"}
        
        await view_welcome_message(mock_ctx)
        
        mock_messages_collection.find_one.assert_called_once_with(
            {"_id": f"welcome_message_{mock_ctx.guild.id}"}
        )
        mock_ctx.send.assert_called_once_with("Current welcome message: Custom Welcome!")


@pytest.mark.asyncio
async def test_view_welcome_message_without_existing_message(mock_ctx):
    with patch('bot.messages_collection') as mock_messages_collection:
        mock_messages_collection.find_one.return_value = None
        
        await view_welcome_message(mock_ctx)
        
        mock_ctx.send.assert_called_once_with("Current welcome message: Welcome to the server! 🎉")


@pytest.mark.asyncio
async def test_on_member_join(mocker):
    member = mocker.Mock(spec=Member)
    member.guild = mocker.Mock()
    member.guild.id = 123456789
    member.name = "TestUser"
    member.mention = "@TestUser"
    
    general_channel = mocker.Mock(spec=TextChannel)
    general_channel.send = AsyncMock()
    
    member.guild.text_channels = [general_channel]
    member.send = AsyncMock()
    
    with patch('discord.utils.get', return_value=general_channel):
        with patch('bot.messages_collection') as mock_messages_collection:
            mock_messages_collection.find_one.return_value = {"message": "Custom Welcome!"}
            
            await on_member_join(member)
            
            general_channel.send.assert_called_once_with("Custom Welcome!")
            member.send.assert_called_once_with(
                "Hi TestUser, welcome to our Discord server! Feel free to ask if you need any help."
            )


@pytest.mark.asyncio
async def test_ping_command(mock_ctx, mocker):
    mock_bot = mocker.patch("bot.bot", autospec=True)
    mock_bot.latency = 0.123

    await ping(mock_ctx)

    mock_ctx.send.assert_called_once()
    assert "Pong! Latency is 123ms" in mock_ctx.send.call_args[0][0]


@pytest.mark.asyncio
async def test_hello_command(mock_ctx):
    await hello(mock_ctx)
    mock_ctx.send.assert_called_once_with("Hello!")


@pytest.mark.asyncio
async def test_inspire_command(mock_ctx, mock_quotes_collection):
    mock_quotes_collection.aggregate.return_value = iter(
        [{"text": "Stay positive.", "author": "Anonymous"}])

    await inspire(mock_ctx)

    mock_ctx.send.assert_called_once_with('"Stay positive." - Anonymous')


@pytest.mark.asyncio
async def test_inspire_command_no_quotes(mock_ctx, mock_quotes_collection):
    mock_quotes_collection.aggregate.return_value = iter([])

    await inspire(mock_ctx)

    mock_ctx.send.assert_called_once_with("Sorry, I couldn't find any quotes.")


@pytest.mark.asyncio
async def test_ask_command(mock_ctx, mock_conversations_collection):
    await ask(mock_ctx)

    mock_ctx.send.assert_called_once_with("Fire away!")

    mock_conversations_collection.update_one.assert_called_once_with(
        {"user_id": mock_ctx.author.id}, {"$set": {"messages": []}}, upsert=True
    )


@pytest.mark.asyncio
async def test_set_newyear_message_with_permissions(mock_ctx):
    mock_ctx.author.guild_permissions.administrator = True
    
    with patch('bot.messages_collection') as mock_messages_collection:
        await set_newyear_message(mock_ctx, message="Happy New Year 2025!")
        
        mock_messages_collection.update_one.assert_called_once_with(
            {"_id": f"new_year_message_{mock_ctx.guild.id}"},
            {"$set": {"message": "Happy New Year 2025!"}},
            upsert=True
        )
        mock_ctx.send.assert_called_once_with("New Year's message updated to: Happy New Year 2025!")


@pytest.mark.asyncio
async def test_set_newyear_message_without_permissions(mock_ctx):
    mock_ctx.author.guild_permissions.administrator = False
    
    # Create a MissingPermissions error
    error = MissingPermissions(['administrator'])
    
    # Test the error handler directly
    await set_newyear_message_error(mock_ctx, error)
    
    # Check if the correct error message was sent
    mock_ctx.send.assert_called_once_with("You do not have the correct permissions to use this command.")

@pytest.mark.asyncio
async def test_view_newyear_message_with_custom_message(mock_ctx):
    with patch('bot.messages_collection') as mock_messages_collection:
        mock_messages_collection.find_one.return_value = {
            "message": "Happy New Year, everyone!"
        }
        
        await view_newyear_message(mock_ctx)
        
        mock_messages_collection.find_one.assert_called_once_with(
            {"_id": f"new_year_message_{mock_ctx.guild.id}"}
        )
        mock_ctx.send.assert_called_once_with(
            "Current New Year's message: Happy New Year, everyone!"
        )


@pytest.mark.asyncio
async def test_view_newyear_message_with_default_message(mock_ctx):
    with patch('bot.messages_collection') as mock_messages_collection:
        mock_messages_collection.find_one.return_value = None
        
        await view_newyear_message(mock_ctx)
        
        mock_messages_collection.find_one.assert_called_once_with(
            {"_id": f"new_year_message_{mock_ctx.guild.id}"}
        )
        mock_ctx.send.assert_called_once_with(
            "Current New Year's message: 🎉 Happy New Year, everyone! Let's celebrate together and make this year amazing! 🎆"
        )


@pytest.mark.asyncio
async def test_check_new_year_message_sent(mocker, mock_messages_collection):
    mock_channel = mocker.Mock()
    mock_channel.name = "general"
    mock_channel.send = AsyncMock()

    mock_bot = mocker.Mock()
    mock_bot.get_all_channels.return_value = [mock_channel]
    mock_bot.wait_until_ready = AsyncMock()
    mock_bot.is_closed.return_value = False

    with patch('bot.bot', mock_bot), \
            patch('bot.datetime') as mock_datetime, \
            patch('bot.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:

        # Set up mock to return True first time, False second time
        mock_bot.is_closed.side_effect = [False, True]
        mock_datetime.now.return_value = datetime(2024, 1, 1, 0, 0, 0)
        
        # Mock the message loading
        mock_messages_collection.find_one.return_value = {"message": "Happy New Year!"}

        await check_new_year()

        mock_channel.send.assert_called_once_with("Happy New Year!")
        mock_sleep.assert_called_once_with(3600)


@pytest.mark.asyncio
async def test_check_new_year_no_message(mocker):
    mock_channel = mocker.Mock()
    mock_channel.name = "general"
    mock_channel.send = AsyncMock()

    mock_bot = mocker.Mock()
    mock_bot.get_all_channels.return_value = [mock_channel]
    mock_bot.wait_until_ready = AsyncMock()
    mock_bot.is_closed.return_value = False

    with patch('bot.bot', mock_bot), \
            patch('bot.datetime') as mock_datetime, \
            patch('bot.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:

        # Set up mock to return True first time, False second time
        mock_bot.is_closed.side_effect = [False, True]
        # Set date to non-New Year's time
        mock_datetime.now.return_value = datetime(2024, 2, 1, 0, 0, 0)

        await check_new_year()

        mock_channel.send.assert_not_called()
        mock_sleep.assert_called_once_with(3600)