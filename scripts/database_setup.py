import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
# Ensure the src folder is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from logger import get_logger  # Use get_logger function

class DatabaseManager:
    def __init__(self):
        """Initialize Database Manager with environment variables and logger."""
        self.logger = get_logger("database_setup")
        self.load_env_variables()
        self.engine = self.get_db_connection()

    def load_env_variables(self):
        """Load database credentials from .env file."""
        load_dotenv("./.env")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_PORT = os.getenv("DB_PORT")

    def get_db_connection(self):
        """Create and return a PostgreSQL database engine."""
        try:
            DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))  # Test connection
            self.logger.info("Successfully connected to the PostgreSQL database.")
            return engine
        except Exception as e:
            self.logger.error(f" Database connection failed: {e}")
            raise

    def create_table(self):
        """Create `telegram_messages` table if it does not exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id SERIAL PRIMARY KEY,
            channel_title TEXT,
            channel_username TEXT,
            message_id BIGINT UNIQUE,
            message TEXT,
            message_date TIMESTAMP,
            media_path TEXT,
            emoji_used TEXT,
            youtube_links TEXT
        );
        """
        try:
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                connection.execute(text(create_table_query))
            self.logger.info("Table 'telegram_messages' created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise

    def insert_data(self, cleaned_df):
        """Insert cleaned Telegram data into PostgreSQL database."""
        try:
            if cleaned_df.empty:
                self.logger.warning("No data to insert. Skipping insertion.")
                return
            
            # Convert NaT timestamps to None (NULL in SQL)
            cleaned_df["message_date"] = cleaned_df["message_date"].apply(lambda x: None if pd.isna(x) else str(x))

            with self.engine.begin() as connection:
                cleaned_df.to_sql("telegram_messages", connection, if_exists="append", index=False, method="multi")

            self.logger.info(f"{len(cleaned_df)} records inserted into PostgreSQL database.")
        except Exception as e:
            self.logger.error(f"Error inserting data: {e}")
            raise

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.create_table()

    # Assuming cleaned data is already available
    cleaned_data_path = "./data/processed/cleaned_data.csv"
    if os.path.exists(cleaned_data_path):
        df_cleaned = pd.read_csv(cleaned_data_path)
        db_manager.insert_data(df_cleaned)
    else:
        db_manager.logger.warning("No cleaned data file found. Skipping insertion.")
