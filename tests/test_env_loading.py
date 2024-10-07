import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file for testing
load_dotenv()

def test_load_environment_variables():
    DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    MONGODB_URI = os.getenv("MONGODB_URI")

    # Check that environment variables are loaded
    assert DISCORD_TOKEN is not None, "DISCORD_TOKEN should not be None"
    assert MONGODB_URI is not None, "MONGODB_URI should not be None"
