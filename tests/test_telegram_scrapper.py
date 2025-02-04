import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import os
import json
import logging
from io import StringIO
# Ensure the src folder is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from telegram_scrapper import get_last_processed_id, save_last_processed_id, scrape_channel, save_messages_to_csv  # Replace 'your_module' with actual module name

# Mock environment variables and logging
@pytest.fixture
def mock_env_vars():
    with mock.patch.dict(os.environ, {"API_ID": "dummy_api_id", "API_HASH": "dummy_api_hash", "PHONE": "dummy_phone_number"}):
        yield

@pytest.fixture
def mock_logger():
    logger = MagicMock()
    yield logger

# Test get_last_processed_id function
def test_get_last_processed_id(mock_logger):
    # Test when file exists
    with mock.patch("builtins.open", mock.mock_open(read_data='{"last_id": 123}')):
        result = get_last_processed_id("test_channel")
        assert result == 123

    # Test when file does not exist
    with mock.patch("builtins.open", mock.mock_open(), create=True):
        result = get_last_processed_id("test_channel")
        assert result == 0
        mock_logger.warning.assert_called_once_with("No last ID file found for test_channel. Starting from 0.")

# Test save_last_processed_id function
def test_save_last_processed_id(mock_logger):
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        save_last_processed_id("test_channel", 123)
        mock_file.assert_called_once_with("test_channel_last_id.json", 'w')
        mock_file().write.assert_called_once_with('{"last_id": 123}')
        mock_logger.info.assert_called_once_with("Saved last processed ID 123 for test_channel.")

# Test scrape_channel function
@pytest.mark.asyncio
async def test_scrape_channel(mock_env_vars, mock_logger):
    # Mock the Telegram client and its methods
    mock_client = AsyncMock()
    mock_entity = MagicMock()
    mock_entity.title = "Test Channel"
    mock_client.get_entity = AsyncMock(return_value=mock_entity)
    mock_client.iter_messages = AsyncMock(return_value=iter([
        MagicMock(id=1, text="Test message", media=None, date="2025-02-04"),
        MagicMock(id=2, text="Test message with photo", media=MagicMock(photo="photo"), date="2025-02-04")
    ]))

    # Mock the download_media method
    mock_client.download_media = AsyncMock()

    all_messages = []

    # Test for @CheMeds channel scraping
    await scrape_channel(mock_client, '@CheMeds', all_messages)

    # Check if messages and images are processed correctly
    assert len(all_messages) == 2  # Two messages should be added
    mock_client.download_media.assert_called_once_with(
        MagicMock(photo="photo"), os.path.join('./data/photos/CheMeds', '@CheMeds_2.jpg')
    )

# Test save_messages_to_csv function
def test_save_messages_to_csv(mock_logger):
    all_messages = [
        ["Test Channel", "@Test", 1, "Test message", "2025-02-04"],
        ["Test Channel", "@Test", 2, "Another message", "2025-02-04"]
    ]

    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        save_messages_to_csv(all_messages)
        mock_file.assert_called_once_with('./data/raw/scraped_data.csv', 'w', newline='', encoding='utf-8')
        mock_logger.info.assert_called_once_with("Saved all messages to scraped_data.csv.")

# Test for error handling in the main function (scraping failure)
@pytest.mark.asyncio
async def test_main_scraping_error(mock_env_vars, mock_logger):
    mock_client = AsyncMock()
    mock_client.start = AsyncMock(side_effect=Exception("Failed to start"))

    with pytest.raises(Exception):
        await main()  # Assuming main() is also wrapped in an async function and tested here
    mock_logger.error.assert_called_once_with("Error in main function: Failed to start")
