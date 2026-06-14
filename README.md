# Grand Horizon - Hotel Management & Booking System

A premium, modern Python-based web application for hotel reception desks. It features a responsive, dark-themed dashboard, real-time occupancy statistics, and direct PostgreSQL database synchronization to manage room directories and bookings.

---

## Scope of the Project

- **Receptionist Dashboard**: Real-time calculations of total rooms, active occupancies, maintenance statuses, and an interactive SVG occupancy rate tracker.
- **Rooms Directory**: Interactive inventory list displaying room types, price per night, status badges (Available, Occupied, Cleaning, Maintenance), and list tags of available room amenities.
- **PostgreSQL Database Storage**: Custom schema to store, update, and fetch room details from a local PostgreSQL database with automatic table creation and data seeding.
- **Graceful Fallback Mode**: The application runs seamlessly even if PostgreSQL is offline by utilizing a local mock data engine.
- **Modern User Experience**: Handcrafted responsive interface styled with glassmorphic cards, transition animations, and high-fidelity layouts (no templates, styled with vanilla HSL CSS and Lucide vector icons).

---

## Technical Stack

- **Backend**: Python 3.x, Flask (3.0.0+)
- **Database**: PostgreSQL (12+), `psycopg2-binary` (2.9.9+)
- **Frontend**: HTML5, Jinja2 Templates, Vanilla CSS (HSL Custom Properties)
- **Icons**: Lucide Vector Icons Library

---

## Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.x** and **PostgreSQL** installed and running on your local machine.

### 2. Clone the Repository
```bash
git clone https://github.com/Manikantamani006/oyo-booking-system.git
cd oyo-booking-system
```

### 3. Install Dependencies
Install Flask and the PostgreSQL database adapter using the requirements file:
```bash
pip install -r requirements.txt
```

### 4. Database Initialization
Make sure your PostgreSQL instance is running on port **5432** under the user **postgres** (with password `postgres` or configured via environment variables).

Execute the database setup script to create the `hotel_management` database, build the tables, and seed initial records:
```bash
python setup_db.py
```

### 5. Running the Application
Launch the Flask development server:
```bash
python app.py
```

The application will start running on:
`http://127.0.0.1:5000`

---

## Project Structure

```text
├── app.py                # Main Flask application and endpoint routers
├── db.py                 # PostgreSQL database connection builder utility
├── setup_db.py           # Database auto-creation and seeding script
├── requirements.txt      # Python package dependencies
├── README.md             # Project documentation and guide
├── static/
│   └── css/
│       └── style.css     # Premium custom UI design sheet
└── templates/
    ├── index.html        # Front-desk receptionist dashboard page
    └── rooms.html        # Room listing and status view page
```

---

## Environment Configuration
You can customize database connection parameters using the following environment variables:
- `DB_NAME`: Database name (defaults to `hotel_management`)
- `DB_USER`: Database username (defaults to `postgres`)
- `DB_PASSWORD`: Database password (defaults to `postgres`)
- `DB_HOST`: Database host address (defaults to `localhost`)
- `DB_PORT`: Database port number (defaults to `5432`)
- `PORT`: Web server running port (defaults to `5000`)
