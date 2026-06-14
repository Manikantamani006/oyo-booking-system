import os
from flask import Flask, render_template
from db import get_db_connection

app = Flask(__name__)

# Mock list of dictionary objects representing hotel rooms
MOCK_ROOMS = [
    {
        "room_number": "101",
        "room_type": "Deluxe Suite",
        "price": 180.0,
        "status": "Available",
        "amenities": ["King Bed", "Ocean View", "Mini Bar", "Free Wi-Fi"],
        "max_occupancy": 2,
        "floor": 1
    },
    {
        "room_number": "102",
        "room_type": "Standard Double",
        "price": 120.0,
        "status": "Occupied",
        "amenities": ["Queen Bed", "City View", "Free Wi-Fi"],
        "max_occupancy": 2,
        "floor": 1
    },
    {
        "room_number": "201",
        "room_type": "Executive Suite",
        "price": 285.0,
        "status": "Available",
        "amenities": ["King Bed", "Balcony", "Free Wi-Fi", "Coffee Station", "Work Desk"],
        "max_occupancy": 3,
        "floor": 2
    },
    {
        "room_number": "202",
        "room_type": "Standard Single",
        "price": 85.0,
        "status": "Maintenance",
        "amenities": ["Single Bed", "Free Wi-Fi"],
        "max_occupancy": 1,
        "floor": 2
    },
    {
        "room_number": "301",
        "room_type": "Presidential Penthouse",
        "price": 650.0,
        "status": "Available",
        "amenities": ["Grand King Bed", "Private Terrace", "Panoramic View", "Kitchenette", "Jacuzzi"],
        "max_occupancy": 4,
        "floor": 3
    },
    {
        "room_number": "302",
        "room_type": "Family Suite",
        "price": 220.0,
        "status": "Cleaning",
        "amenities": ["2 Queen Beds", "Kitchenette", "Free Wi-Fi", "Living Area"],
        "max_occupancy": 4,
        "floor": 3
    }
]

@app.route("/")
def index():
    """
    Renders the reception dashboard.
    Computes real-time statistics from the room data.
    """
    rooms_list = MOCK_ROOMS
    db_connected = False
    
    # Attempt to load dynamic data from the database if connected
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT room_number, room_type, price, status, amenities, max_occupancy, floor FROM rooms ORDER BY room_number;")
        db_rooms = cur.fetchall()
        cur.close()
        conn.close()
        if db_rooms:
            rooms_list = db_rooms
        db_connected = True
    except Exception as e:
        # Gracefully handle database absence by falling back to mock data
        print(f"[DB Notice] Using fallback mock data. Reason: {e}")
        db_connected = False
    
    # Calculate key reception metrics
    stats = {
        "total_rooms": len(rooms_list),
        "available_rooms": sum(1 for r in rooms_list if r["status"].lower() == "available"),
        "occupied_rooms": sum(1 for r in rooms_list if r["status"].lower() == "occupied"),
        "cleaning_rooms": sum(1 for r in rooms_list if r["status"].lower() == "cleaning"),
        "maintenance_rooms": sum(1 for r in rooms_list if r["status"].lower() == "maintenance"),
    }
    
    # Calculate occupancy rate percentage
    if stats["total_rooms"] > 0:
        stats["occupancy_rate"] = round((stats["occupied_rooms"] / stats["total_rooms"]) * 100, 1)
    else:
        stats["occupancy_rate"] = 0.0
        
    return render_template("index.html", stats=stats, db_connected=db_connected)

@app.route("/rooms")
def rooms():
    """
    Renders the rooms management interface.
    Fetches room records from PostgreSQL using a SELECT * query.
    """
    rooms_list = MOCK_ROOMS
    db_connected = False
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Execute SELECT * query to fetch all columns
        cur.execute("SELECT * FROM rooms ORDER BY room_number;")
        db_rooms = cur.fetchall()
        
        # Convert rows and parse amenities string if needed
        parsed_rooms = []
        for r in db_rooms:
            room_dict = dict(r)
            amenities = room_dict.get("amenities", "")
            if isinstance(amenities, str):
                room_dict["amenities"] = [a.strip() for a in amenities.split(",") if a.strip()]
            else:
                room_dict["amenities"] = list(amenities) if amenities else []
            parsed_rooms.append(room_dict)
            
        cur.close()
        conn.close()
        
        if parsed_rooms:
            rooms_list = parsed_rooms
        db_connected = True
    except Exception as e:
        print(f"[DB Error] Failed to retrieve records from PostgreSQL database: {e}")
        rooms_list = MOCK_ROOMS
        db_connected = False

    return render_template("rooms.html", rooms=rooms_list, db_connected=db_connected)


if __name__ == "__main__":
    # Allow port and host customization via env vars
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
