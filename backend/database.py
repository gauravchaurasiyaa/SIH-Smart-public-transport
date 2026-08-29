import sqlite3
from datetime import datetime, timedelta

DB_NAME = "smartbus.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT NOT NULL,
            route_number TEXT NOT NULL,
            route_name TEXT NOT NULL,
            current_location TEXT,
            next_stop TEXT,
            eta INTEGER DEFAULT 0,
            occupancy INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Active'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT,
            route_number TEXT,
            from_location TEXT,
            to_location TEXT,
            fare REAL,
            travel_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT,
            route_number TEXT,
            fare REAL,
            travel_date TEXT
        )
    """)

    connection.commit()

    add_sample_buses(connection)
    add_sample_travel_data(connection)

    connection.close()


# =====================================
# SAMPLE BUS DATA
# =====================================

def add_sample_buses(connection):

    cursor = connection.cursor()

    count = cursor.execute(
        "SELECT COUNT(*) FROM buses"
    ).fetchone()[0]

    if count > 0:
        return

    buses = [

        (
            "UP 53 NC 2456",
            "NH24",
            "Ghaziabad - Delhi",
            "Ghaziabad",
            "Anand Vihar",
            8,
            35,
            "Active"
        ),

        (
            "UP 53 AB 7821",
            "NH24",
            "Ghaziabad - Delhi",
            "Vijay Nagar",
            "Anand Vihar",
            14,
            62,
            "Active"
        ),

        (
            "UP 53 CD 4512",
            "NH24",
            "Ghaziabad - Delhi",
            "Crossings Republik",
            "Ghaziabad",
            20,
            48,
            "Active"
        ),

        (
            "UP 53 NC 9090",
            "NH28",
            "Lucknow - Gorakhpur",
            "Ayodhya",
            "Basti",
            25,
            72,
            "Active"
        ),

        (
            "UP 53 VIP 0001",
            "NH28",
            "Lucknow - Gorakhpur",
            "Basti",
            "Khalilabad",
            12,
            41,
            "Active"
        ),

        (
            "UP 53 XY 6634",
            "NH28",
            "Lucknow - Gorakhpur",
            "Khalilabad",
            "Gorakhpur",
            18,
            56,
            "Active"
        ),

        (
            "UP 53 MN 3188",
            "NH91",
            "Kanpur - Aligarh",
            "Kanpur",
            "Etawah",
            17,
            38,
            "Active"
        ),

        (
            "UP 53 ZZ 7777",
            "NH91",
            "Kanpur - Aligarh",
            "Etawah",
            "Mainpuri",
            29,
            81,
            "Active"
        )

    ]

    cursor.executemany("""
        INSERT INTO buses (
            bus_number,
            route_number,
            route_name,
            current_location,
            next_stop,
            eta,
            occupancy,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, buses)

    connection.commit()


# =====================================
# SAMPLE TRAVEL + EXPENSE DATA
# =====================================

def add_sample_travel_data(connection):

    cursor = connection.cursor()

    count = cursor.execute(
        "SELECT COUNT(*) FROM travel_history"
    ).fetchone()[0]

    if count > 0:
        return

    today = datetime.now()

    trips = [

        (
            "UP 53 NC 2456",
            "NH24",
            "Ghaziabad",
            "Anand Vihar",
            35,
            (today - timedelta(days=1)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 AB 7821",
            "NH24",
            "Vijay Nagar",
            "Anand Vihar",
            30,
            (today - timedelta(days=2)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 CD 4512",
            "NH24",
            "Crossings Republik",
            "Ghaziabad",
            25,
            (today - timedelta(days=3)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 VIP 0001",
            "NH28",
            "Basti",
            "Khalilabad",
            45,
            (today - timedelta(days=5)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 XY 6634",
            "NH28",
            "Khalilabad",
            "Gorakhpur",
            50,
            (today - timedelta(days=7)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 MN 3188",
            "NH91",
            "Kanpur",
            "Etawah",
            40,
            (today - timedelta(days=10)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 ZZ 7777",
            "NH91",
            "Etawah",
            "Mainpuri",
            45,
            (today - timedelta(days=14)).strftime("%Y-%m-%d")
        ),

        (
            "UP 53 NC 2456",
            "NH24",
            "Ghaziabad",
            "Anand Vihar",
            35,
            (today - timedelta(days=20)).strftime("%Y-%m-%d")
        )

    ]

    cursor.executemany("""
        INSERT INTO travel_history (
            bus_number,
            route_number,
            from_location,
            to_location,
            fare,
            travel_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, trips)


    cursor.executemany("""
        INSERT INTO expenses (
            bus_number,
            route_number,
            fare,
            travel_date
        )
        VALUES (?, ?, ?, ?)
    """, [

        (
            trip[0],
            trip[1],
            trip[4],
            trip[5]
        )

        for trip in trips

    ])

    connection.commit()


# =====================================
# GET ALL BUSES
# =====================================

def get_all_buses():

    connection = get_connection()

    buses = connection.execute(
        "SELECT * FROM buses ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return [
        dict(bus)
        for bus in buses
    ]


# =====================================
# TRAVEL HISTORY
# =====================================

def get_travel_history():

    connection = get_connection()

    history = connection.execute("""
        SELECT
            bus_number,
            route_number,
            from_location,
            to_location,
            fare,
            travel_date
        FROM travel_history
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [
        dict(item)
        for item in history
    ]


# =====================================
# ADD BUS
# =====================================

def add_bus(
    bus_number,
    route_number,
    route_name,
    current_location,
    next_stop,
    eta,
    occupancy,
    status="Active"
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO buses (
            bus_number,
            route_number,
            route_name,
            current_location,
            next_stop,
            eta,
            occupancy,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bus_number,
        route_number,
        route_name,
        current_location,
        next_stop,
        eta,
        occupancy,
        status
    ))

    connection.commit()
    connection.close()


# =====================================
# ADD TRAVEL
# =====================================

def add_travel(
    bus_number,
    route_number,
    from_location,
    to_location,
    fare,
    travel_date
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO travel_history (
            bus_number,
            route_number,
            from_location,
            to_location,
            fare,
            travel_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        bus_number,
        route_number,
        from_location,
        to_location,
        fare,
        travel_date
    ))

    connection.execute("""
        INSERT INTO expenses (
            bus_number,
            route_number,
            fare,
            travel_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        bus_number,
        route_number,
        fare,
        travel_date
    ))

    connection.commit()
    connection.close()


# =====================================
# EXPENSE SUMMARY
# =====================================

def get_expense_summary():

    connection = get_connection()

    weekly = connection.execute("""
        SELECT
            COALESCE(SUM(fare), 0) AS expense,
            COUNT(*) AS trips
        FROM expenses
        WHERE date(travel_date)
        >= date('now', '-7 days')
    """).fetchone()


    monthly = connection.execute("""
        SELECT
            COALESCE(SUM(fare), 0) AS expense,
            COUNT(*) AS trips
        FROM expenses
        WHERE date(travel_date)
        >= date('now', 'start of month')
    """).fetchone()


    average = connection.execute("""
        SELECT
            COALESCE(AVG(fare), 0) AS average
        FROM expenses
    """).fetchone()


    connection.close()


    return {

        "weekly": {
            "expense": weekly["expense"],
            "trips": weekly["trips"]
        },

        "monthly": {
            "expense": monthly["expense"],
            "trips": monthly["trips"]
        },

        "average_per_trip":
            average["average"]

    }


# =====================================
# INITIALIZE
# =====================================

if __name__ == "__main__":

    init_database()

    print(
        "Smart Bus database initialized successfully."
    )

    print(
        "Sample buses and travel data added."
    )