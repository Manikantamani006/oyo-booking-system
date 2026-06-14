import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Establishes and returns a connection to the local PostgreSQL database.
    
    Database Name: hotel_management
    Port: 5432
    User: postgres
    """
    # Load configuration from environment variables with defaults matching user requirements
    dbname = os.environ.get("DB_NAME", "hotel_eye")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        cursor_factory=RealDictCursor
    )
    return conn
