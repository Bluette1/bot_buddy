import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from flask import url_for
from bot import FlaskServer

@pytest.fixture
def bot(mocker):
    return mocker.AsyncMock()

@pytest.fixture
def app(bot):
    # Mock the bot and its methods
    mock_bot = AsyncMock()
    mock_bot.get_guild.return_value = MagicMock()
    mock_bot.get_channel.return_value = AsyncMock()

    # Instantiate the FlaskServer with mocks
    flask_server = FlaskServer(mock_bot, guild_id=123, role_id=456, premier_channel_id=789)
    return flask_server.app

def test_kofi_webhook(client, bot):
    # Mock data for the webhook
    data = {
        'from_name': 'TestDonor',
        'amount': '5',
        'message': 'Keep up the great work!'
    }

    # Mock the process_donation method
    with patch.object(FlaskServer, 'process_donation', new_callable=AsyncMock) as mock_process_donation:
        # Call the webhook
        response = client.post(url_for('kofi_webhook'), json=data)

        # Check the response
        assert response.status_code == 200
        assert response.json == {'status': 'success'}

        # Verify the process_donation task was called
        mock_process_donation.assert_called_once_with('TestDonor', '5', 'Keep up the great work!')