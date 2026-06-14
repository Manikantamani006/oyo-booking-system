import os
from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection

class RoomDict(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            # Mapping index positions to dictionary keys
            keys_order = ["id", "room_number", "room_type", "price", "status", "max_occupancy", "floor", "amenities", "guest_name", "guest_phone"]
            if 0 <= key < len(keys_order):
                return self.get(keys_order[key])
        return super().__getitem__(key)

app = Flask(__name__)

# Mock list of dictionary objects representing hotel rooms
MOCK_ROOMS = [
    {
        "id": 1,
        "room_number": "101",
        "room_type": "Deluxe Suite",
        "price": 180.0,
        "status": "Available",
        "amenities": ["King Bed", "Ocean View", "Mini Bar", "Free Wi-Fi"],
        "max_occupancy": 2,
        "floor": 1
    },
    {
        "id": 2,
        "room_number": "102",
        "room_type": "Standard Double",
        "price": 120.0,
        "status": "Occupied",
        "amenities": ["Queen Bed", "City View", "Free Wi-Fi"],
        "max_occupancy": 2,
        "floor": 1
    },
    {
        "id": 3,
        "room_number": "201",
        "room_type": "Executive Suite",
        "price": 285.0,
        "status": "Available",
        "amenities": ["King Bed", "Balcony", "Free Wi-Fi", "Coffee Station", "Work Desk"],
        "max_occupancy": 3,
        "floor": 2
    },
    {
        "id": 4,
        "room_number": "202",
        "room_type": "Standard Single",
        "price": 85.0,
        "status": "Maintenance",
        "amenities": ["Single Bed", "Free Wi-Fi"],
        "max_occupancy": 1,
        "floor": 2
    },
    {
        "id": 5,
        "room_number": "301",
        "room_type": "Presidential Penthouse",
        "price": 650.0,
        "status": "Available",
        "amenities": ["Grand King Bed", "Private Terrace", "Panoramic View", "Kitchenette", "Jacuzzi"],
        "max_occupancy": 4,
        "floor": 3
    },
    {
        "id": 6,
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
        cur.execute("SELECT * FROM rooms ORDER BY room_number;")
        db_rooms = cur.fetchall()
        
        parsed_rooms = []
        for r in db_rooms:
            room_dict = RoomDict(r)
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
        # Gracefully handle database absence by falling back to mock data
        print(f"[DB Notice] Using fallback mock data. Reason: {e}")
        db_connected = False
    
    rooms_list = [RoomDict(r) for r in rooms_list]
    
    # Calculate key reception metrics
    stats = {
        "total_rooms": len(rooms_list),
        "available_rooms": sum(1 for r in rooms_list if r["status"].lower() == "available"),
        "occupied_rooms": sum(1 for r in rooms_list if (r["status"].lower() == "occupied" or r["status"].lower() == "booked")),
        "cleaning_rooms": sum(1 for r in rooms_list if r["status"].lower() == "cleaning"),
        "maintenance_rooms": sum(1 for r in rooms_list if r["status"].lower() == "maintenance"),
    }
    
    # Calculate occupancy rate percentage
    if stats["total_rooms"] > 0:
        stats["occupancy_rate"] = round((stats["occupied_rooms"] / stats["total_rooms"]) * 100, 1)
    else:
        stats["occupancy_rate"] = 0.0
        
    return render_template("index.html", stats=stats, db_connected=db_connected, rooms=rooms_list)

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
            room_dict = RoomDict(r)
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

    rooms_list = [RoomDict(r) for r in rooms_list]
    return render_template("rooms.html", rooms=rooms_list, db_connected=db_connected)


@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    db_connected = False
    room = None
    
    if request.method == 'POST':
        guest_name = request.form.get('guest_name')
        guest_phone = request.form.get('guest_phone')
        try:
            price = int(float(request.form.get('price', 0)))
        except ValueError:
            price = 0
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE rooms 
                SET status = 'Booked', 
                    guest_name = %s, 
                    guest_phone = %s, 
                    price = %s 
                WHERE id = %s;
            """, (guest_name, guest_phone, price, room_id))
            conn.commit()
            cur.close()
            conn.close()
            db_connected = True
        except Exception as e:
            print(f"[DB Error] Failed to book room: {e}")
            # Mock update fallback
            for r in MOCK_ROOMS:
                if r.get("id") == room_id:
                    r["status"] = "Booked"
                    r["guest_name"] = guest_name
                    r["guest_phone"] = guest_phone
                    r["price"] = float(price)
                    break
        return redirect(url_for('rooms'))
        
    else: # GET method
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM rooms WHERE id = %s;", (room_id,))
            room = cur.fetchone()
            cur.close()
            conn.close()
            db_connected = True
            
            if room:
                room = dict(room)
                # Parse amenities just in case
                amenities = room.get("amenities", "")
                if isinstance(amenities, str):
                    room["amenities"] = [a.strip() for a in amenities.split(",") if a.strip()]
                else:
                    room["amenities"] = list(amenities) if amenities else []
        except Exception as e:
            print(f"[DB Error] Failed to fetch room details for booking: {e}")
            db_connected = False
            
        # Fallback to mock data if DB failed or room wasn't found in DB
        if not room:
            for r in MOCK_ROOMS:
                if r.get("id") == room_id:
                    room = r
                    break
                    
        if not room:
            return "Room not found", 404
            
        room = RoomDict(room)
        return render_template('book.html', room=room, db_connected=db_connected)


@app.route("/add-room", methods=["POST"])
def add_room():
    room_number = request.form.get("room_number")
    room_type = request.form.get("room_type")
    try:
        price = int(float(request.form.get("price", 0)))
    except ValueError:
        price = 0
    status = request.form.get("status", "Available")
    try:
        floor = int(request.form.get("floor", 1))
    except ValueError:
        floor = 1
    try:
        max_occupancy = int(request.form.get("max_occupancy", 2))
    except ValueError:
        max_occupancy = 2
    amenities = request.form.get("amenities", "")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rooms (room_number, room_type, price, status, floor, max_occupancy, amenities)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (room_number, room_type, price, status, floor, max_occupancy, amenities))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Failed to insert room: {e}")
        # Fallback mock update
        MOCK_ROOMS.append({
            "id": len(MOCK_ROOMS) + 1,
            "room_number": room_number,
            "room_type": room_type,
            "price": float(price),
            "status": status,
            "floor": floor,
            "max_occupancy": max_occupancy,
            "amenities": [a.strip() for a in amenities.split(",") if a.strip()],
            "guest_name": None,
            "guest_phone": None
        })
    return redirect(url_for("index"))


@app.route("/update-room/<int:room_id>", methods=["POST"])
def update_room(room_id):
    room_number = request.form.get("room_number")
    room_type = request.form.get("room_type")
    try:
        price = int(float(request.form.get("price", 0)))
    except ValueError:
        price = 0
    status = request.form.get("status", "Available")
    try:
        floor = int(request.form.get("floor", 1))
    except ValueError:
        floor = 1
    try:
        max_occupancy = int(request.form.get("max_occupancy", 2))
    except ValueError:
        max_occupancy = 2
    amenities = request.form.get("amenities", "")
    guest_name = request.form.get("guest_name") or None
    guest_phone = request.form.get("guest_phone") or None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE rooms 
            SET room_number = %s,
                room_type = %s,
                price = %s,
                status = %s,
                floor = %s,
                max_occupancy = %s,
                amenities = %s,
                guest_name = %s,
                guest_phone = %s
            WHERE id = %s;
        """, (room_number, room_type, price, status, floor, max_occupancy, amenities, guest_name, guest_phone, room_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Failed to update room: {e}")
        # Fallback mock update
        for r in MOCK_ROOMS:
            if r.get("id") == room_id:
                r["room_number"] = room_number
                r["room_type"] = room_type
                r["price"] = float(price)
                r["status"] = status
                r["floor"] = floor
                r["max_occupancy"] = max_occupancy
                r["amenities"] = [a.strip() for a in amenities.split(",") if a.strip()]
                r["guest_name"] = guest_name
                r["guest_phone"] = guest_phone
                break
    return redirect(url_for("index"))


@app.route("/delete-room/<int:room_id>", methods=["GET", "POST"])
def delete_room(room_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM rooms WHERE id = %s;", (room_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Failed to delete room: {e}")
        # Fallback mock delete
        global MOCK_ROOMS
        MOCK_ROOMS = [r for r in MOCK_ROOMS if r.get("id") != room_id]
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Allow port and host customization via env vars
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
