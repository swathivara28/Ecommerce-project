
import psycopg2
import os
from dotenv import load_dotenv

# Load project .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def DatabaseConnection():
    try:
        db_config = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 5432)),
            sslmode="require"
        )

        return db_config

    except Exception as e:
        print(f"Something wrong in database/connection.py: {e}")
        raise
