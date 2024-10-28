# tests/conftest.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import discord
from discord.ext import commands
import discord.ext.test as dpytest
from pymongo import MongoClient
from datetime import datetime
from repositories.birthday_repository import BirthdayRepository

@pytest.fixture
def mock_mongo():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test_discord_bot']
    collection = db['test_birthdays']
    collection.delete_many({})
    return collection

@pytest.fixture
def birthday_repo(mock_mongo):
    return BirthdayRepository(mock_mongo)

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def bot():
    # Create a bot instance for testing
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
    )
    
    await bot._async_setup_hook() 
    return bot

@pytest.fixture
async def setup_bot(bot):
    dpytest.configure(bot)
    return bot
