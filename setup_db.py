import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    # Load database settings from environment variables with defaults
    db_name = os.environ.get("DB_NAME", "hotel_management")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")

    print("=== Grand Horizon Hotel Database Setup ===")
    
    # Step 1: Ensure the database exists
    try:
        print(f"Connecting to default 'postgres' database on port {db_port} to check/create target database...")
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Database '{db_name}' does not exist. Creating database...")
            cur.execute(f'CREATE DATABASE {db_name};')
            print(f"Database '{db_name}' successfully created.")
        else:
            print(f"Database '{db_name}' already exists. Proceeding...")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Notice: Initial database presence check could not be completed: {e}")
        print("Will attempt direct connection to target database.")

    # Step 2: Connect to target database and set up tables
    try:
        print(f"\nConnecting to target database '{db_name}' as user '{db_user}'...")
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()

        # Drop rooms table if it exists
        print("Dropping 'rooms' table if it exists...")
        cur.execute("DROP TABLE IF EXISTS rooms;")

        # Create rooms table matching requested columns and app compatibility
        print("Creating 'rooms' table...")
        cur.execute("""
            CREATE TABLE rooms (
                id SERIAL PRIMARY KEY,
                room_number VARCHAR(10) NOT NULL UNIQUE,
                room_type VARCHAR(100) NOT NULL,
                price INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL,
                max_occupancy INTEGER DEFAULT 2,
                floor INTEGER DEFAULT 1,
                amenities VARCHAR(255) DEFAULT ''
            );
        """)
        print("Table 'rooms' created successfully.")

        # Insert 3 sample rooms into the table
        print("Inserting 3 sample room records...")
        sample_rooms = [
            ("101", "Deluxe Suite", 180, "Available", 2, 1, "King Bed, Ocean View, Mini Bar, Free Wi-Fi"),
            ("102", "Standard Double", 120, "Occupied", 2, 1, "Queen Bed, City View, Free Wi-Fi"),
            ("201", "Executive Suite", 285, "Available", 3, 2, "King Bed, Balcony, Free Wi-Fi, Coffee Station, Work Desk")
        ]

        for room in sample_rooms:
            cur.execute("""
                INSERT INTO rooms (room_number, room_type, price, status, max_occupancy, floor, amenities)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, room)
            print(f" - Inserted Room {room[0]} ({room[1]})")

        # Commit transactions and close connections
        conn.commit()
        print("\nAll changes successfully committed to database.")
        
        cur.close()
        conn.close()
        print("Database connection closed cleanly.")
        print("Setup completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: Database setup failed: {e}")
        print("Please verify that PostgreSQL is running locally on the specified port.")

if __name__ == "__main__":
    setup_database()
