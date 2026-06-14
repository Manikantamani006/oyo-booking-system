import os
import psycopg2
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

def upgrade_database():
    db_name = os.environ.get("DB_NAME", "hotel_eye")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")

    print("=== Upgrading Database Schema ===")
    try:
        print(f"Connecting to database '{db_name}' as user '{db_user}'...")
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()
        
        # Alter table rooms to add guest_name and guest_phone
        print("Executing ALTER TABLE rooms statement...")
        cur.execute("""
            ALTER TABLE rooms 
            ADD COLUMN IF NOT EXISTS guest_name VARCHAR(100),
            ADD COLUMN IF NOT EXISTS guest_phone VARCHAR(50);
        """)
        
        conn.commit()
        print("ALTER TABLE rooms command executed successfully!")
        
        cur.close()
        conn.close()
        print("Columns 'guest_name' and 'guest_phone' added successfully. Connection closed.")
        
    except Exception as e:
        print(f"Error during schema upgrade: {e}")

if __name__ == "__main__":
    upgrade_database()
