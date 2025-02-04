import os
import sys
import pandas as pd
import re
import emoji
# Ensure the src folder is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from logger import get_logger  

class DataCleaner:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.logger = get_logger("data_cleaning")  # Use get_logger

    def load_csv(self):
        """ Load CSV file into a Pandas DataFrame. """
        try:
            df = pd.read_csv(self.input_path)
            self.logger.info(f"CSV file '{self.input_path}' loaded successfully.")
            return df
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            raise

    def extract_emojis(self, text):
        """ Extract emojis from text. """
        emojis = ''.join(c for c in text if c in emoji.EMOJI_DATA)
        return emojis if emojis else "No emoji"

    def remove_emojis(self, text):
        """ Remove emojis from the message text. """
        return ''.join(c for c in text if c not in emoji.EMOJI_DATA)

    def extract_youtube_links(self, text):
        """ Extract YouTube links from text. """
        youtube_pattern = r"(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+)"
        links = re.findall(youtube_pattern, text)
        return ', '.join(links) if links else "No YouTube link"

    def remove_youtube_links(self, text):
        """ Remove YouTube links from the message text. """
        youtube_pattern = r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+"
        return re.sub(youtube_pattern, '', text).strip()

    def clean_text(self, text):
        """ Standardize text by removing newline characters and unnecessary spaces. """
        if pd.isna(text):
            return "No Message"
        return re.sub(r'\n+', ' ', text).strip()

    def clean_dataframe(self, df):
        """ Perform all cleaning and standardization steps. """
        try:
            df = df.drop_duplicates(subset=["Message ID"]).copy()
            self.logger.info(" Duplicates removed.")

            df.loc[:, 'Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df.loc[:, 'Date'] = df['Date'].where(df['Date'].notna(), None)
            self.logger.info(" Date column formatted.")

            df.loc[:, 'Message ID'] = pd.to_numeric(df['Message ID'], errors="coerce").fillna(0).astype(int)

            df.loc[:, 'Message'] = df['Message'].fillna("No Message")
            df.loc[:, 'Media Path'] = df['Media Path'].fillna("No Media")

            df.loc[:, 'Channel Title'] = df['Channel Title'].str.strip()
            df.loc[:, 'Channel Username'] = df['Channel Username'].str.strip()
            df.loc[:, 'Message'] = df['Message'].apply(self.clean_text)
            df.loc[:, 'Media Path'] = df['Media Path'].str.strip()

            df.loc[:, 'emoji_used'] = df['Message'].apply(self.extract_emojis)
            df.loc[:, 'Message'] = df['Message'].apply(self.remove_emojis)

            df.loc[:, 'youtube_links'] = df['Message'].apply(self.extract_youtube_links)
            df.loc[:, 'Message'] = df['Message'].apply(self.remove_youtube_links)

            df = df.rename(columns={
                "Channel Title": "channel_title",
                "Channel Username": "channel_username",
                "Message ID": "message_Message ID",
                "Message": "message",
                "Date": "message_date",
                "Media Path": "media_path",
                "emoji_used": "emoji_used",
                "youtube_links": "youtube_links"
            })

            self.logger.info(" Data cleaning completed.")
            return df
        except Exception as e:
            self.logger.error(f" Data cleaning error: {e}")
            raise

    def save_cleaned_data(self, df):
        """ Save cleaned data to a CSV file. """
        try:
            df.to_csv(self.output_path, index=False)
            self.logger.info(f" Cleaned data saved to '{self.output_path}'.")
            print(f" Cleaned data saved to '{self.output_path}'.")
        except Exception as e:
            self.logger.error(f" Error saving cleaned data: {e}")
            raise

    def run(self):
        """ Execute full data cleaning pipeline. """
        df = self.load_csv()
        cleaned_df = self.clean_dataframe(df)
        self.save_cleaned_data(cleaned_df)
        return cleaned_df

# Example usage:
if __name__ == "__main__":
    cleaner = DataCleaner(input_path="./data/raw/scraped_data.csv", output_path="./data/processed/cleaned_data.csv")
    cleaner.run()
