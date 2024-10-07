from bot import bot  # Adjust the import according to your file structure


async def test_bot_initialization():
    assert bot.user is not None
