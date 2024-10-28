
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import FlaskServer

@pytest.fixture
def bot(mocker):
    mock_bot = mocker.AsyncMock()
    mock_bot.loop = MagicMock()
    mock_bot.loop.create_task = lambda x: x
    return mock_bot

@pytest.fixture
def app(bot):
    mock_bot = bot
    mock_bot.guilds = [MagicMock(id=123, name="Test Guild")]
    mock_bot.guilds[0].get_member = AsyncMock(return_value=MagicMock(id=456, name="TestDonor"))
    
    flask_server = FlaskServer(mock_bot)
    return flask_server.app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_kofi_webhook(client, bot):
    data = {
        'from_name': 'TestDonor',
        'amount': '5',
        'message': 'Keep up the great work!'
    }

    with patch.object(FlaskServer, 'process_donation', new_callable=AsyncMock) as mock_process_donation:
        # Make the mock return a coroutine that can be awaited
        mock_process_donation.return_value = None
        
        # Use synchronous post method
        response = client.post('/kofi-webhook', json=data)

        assert response.status_code == 200
        assert response.get_json() == {'status': 'success'}

        # Verify the process_donation was called with correct parameters
        mock_process_donation.assert_called_once_with('TestDonor', '5', 'Keep up the great work!')