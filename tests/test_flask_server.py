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
    mock_bot = bot
    mock_bot.guilds = [MagicMock(id=123, name="Test Guild")]  # Mock a guild for testing
    mock_bot.guilds[0].get_member = AsyncMock(return_value=MagicMock(id=456, name="TestDonor"))  # Mock the member retrieval

    # Instantiate the FlaskServer with mocks
    flask_server = FlaskServer(mock_bot)
    return flask_server.app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

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

        # Verify the process_donation task was called with the correct parameters
        mock_process_donation.assert_called_once_with('TestDonor', '5', 'Keep up the great work!')