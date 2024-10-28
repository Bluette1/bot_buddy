# tests/test_birthday_commands.py
import pytest
import discord.ext.test as dpytest
from commands.birthday_commands import BirthdayCommands
from datetime import datetime

@pytest.mark.asyncio
async def test_set_birthday_command(setup_bot, birthday_repo):
    bot = setup_bot
    commands_cog = BirthdayCommands(bot, birthday_repo)
    await bot.add_cog(commands_cog)
    
    await dpytest.message("!setbirthday 2000-01-01")
    last_message = dpytest.get_message()
    print(f"Actual message: {last_message.content}")
    assert "successfully" in last_message.content.lower()

@pytest.mark.asyncio
async def test_get_birthday_command(setup_bot, birthday_repo):
    bot = setup_bot
    commands_cog = BirthdayCommands(bot, birthday_repo)
    await bot.add_cog(commands_cog)
    
    # Set a birthday first
    await dpytest.message("!setbirthday 2000-01-01")
    dpytest.get_message()  # Clear the message queue
    
    # Get the birthday
    await dpytest.message("!getbirthday")
    last_message = dpytest.get_message()
    print(f"Actual message: {last_message.content}")  # Debug print
    assert "2000-01-01" in last_message.content

@pytest.mark.asyncio
async def test_remove_birthday_command(setup_bot, birthday_repo):
    bot = setup_bot
    commands_cog = BirthdayCommands(bot, birthday_repo)
    await bot.add_cog(commands_cog)
    
    # Set a birthday first
    await dpytest.message("!setbirthday 2000-01-01")
    dpytest.get_message()  # Clear the message queue
    
    # Remove the birthday
    await dpytest.message("!remove_birthday")
    last_message = dpytest.get_message()
    print(f"Actual message: {last_message.content}")  # Debug print
    
    # Make the assertion more flexible
    assert any(phrase in last_message.content.lower() for phrase in [
        "birthday removed",
        "removed successfully",
        "successfully removed",
        "birthday deleted",
        "deleted successfully",
        "successfully deleted",
        "removed from the database"
    ])

    # Verify the birthday was actually removed
    await dpytest.message("!getbirthday")
    last_message = dpytest.get_message()
    assert "you haven\'t set your birthday yet" in last_message.content.lower() or "not set" in last_message.content.lower()