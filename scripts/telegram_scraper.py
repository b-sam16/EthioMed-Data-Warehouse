import os
import csv
import json
import logging
from telethon import TelegramClient
from dotenv import load_dotenv

# Ensure the src folder is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from logger import get_logger  # Import the custom logger from src/logger.py

# Load environment variables
load_dotenv('.env')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE')

# Initialize the logger
logger = get_logger("scraping")

# Ensure the necessary directories exist
os.makedirs('./data/raw', exist_ok=True)
os.makedirs('./data/photos/CheMeds', exist_ok=True)
os.makedirs('./data/photos/lobelia4cosmetics', exist_ok=True)

# Function to get last processed message ID
def get_last_processed_id(channel_username):
    try:
        with open(f"{channel_username}_last_id.json", 'r') as f:
            return json.load(f).get('last_id', 0)
    except FileNotFoundError:
        logger.warning(f"No last ID file found for {channel_username}. Starting from 0.")
        return 0

# Function to save last processed message ID
def save_last_processed_id(channel_username, last_id):
    with open(f"{channel_username}_last_id.json", 'w') as f:
        json.dump({'last_id': last_id}, f)
        logger.info(f"Saved last processed ID {last_id} for {channel_username}.")

# Function to scrape data from a single channel
async def scrape_channel(client, channel_username, all_messages):
    try:
        entity = await client.get_entity(channel_username)
        channel_title = entity.title

        last_id = get_last_processed_id(channel_username)

        # Collect messages and images
        messages = []
        images = []

        async for message in client.iter_messages(entity, limit=100, reverse=True):
            if message.id <= last_id:
                continue
            
            media_path = None  # Default to None if no media

            # Save text messages for all channels in the same CSV
            if message.text:
                all_messages.append([channel_title, channel_username, message.id, message.text, message.date, media_path])

            # Save images (only for specific channels)
            if message.media and hasattr(message.media, 'photo') and channel_username in ['@CheMeds', '@lobelia4cosmetics']:
                # Set the file path for image download
                if channel_username == '@CheMeds':
                    media_path = os.path.join('./data/photos/CheMeds', f"{channel_username}_{message.id}.jpg")
                elif channel_username == '@lobelia4cosmetics':
                    media_path = os.path.join('./data/photos/lobelia4cosmetics', f"{channel_username}_{message.id}.jpg")

                # Download image using Telethon's download_media function
                await client.download_media(message.media, media_path)
                logger.info(f"Downloaded image for {channel_username} to {media_path}")
                
            # Append message with media path
            all_messages.append([channel_title, channel_username, message.id, message.text, message.date, media_path])

            # Update the last processed ID after processing the message
            last_id = message.id
        save_last_processed_id(channel_username, last_id)

    except Exception as e:
        logger.error(f"Error while scraping {channel_username}: {e}")

# Function to save messages to CSV
def save_messages_to_csv(all_messages):
    try:
        with open('./data/raw/scraped_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Channel Title', 'Channel Username', 'Message ID', 'Message', 'Date','Media Path'])
            for message in all_messages:
                writer.writerow(message)
        logger.info(f"Saved all messages to scraped_data.csv.")
    except Exception as e:
        logger.error(f"Error while saving messages to CSV: {e}")

# Initialize the client once with a session file
client = TelegramClient('scraping_session', api_id, api_hash)

async def main():
    try:
        await client.start(phone_number)
        logger.info("Client started successfully.")

        all_messages = []

        channels = [
            '@DoctorsET',
            '@CheMeds',
            '@lobelia4cosmetics',
            '@yetenaweg',
            '@EAHCI'
        ]
        
        for channel in channels:
            await scrape_channel(client, channel, all_messages)

        # Save all messages to a single CSV file
        save_messages_to_csv(all_messages)

    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
