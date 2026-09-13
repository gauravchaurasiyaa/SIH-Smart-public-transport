import sqlite3
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "transport.db"
)


def get_connection():

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id TEXT PRIMARY KEY,
            registration TEXT NOT NULL,
            route_id TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            passengers INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            stops TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stops (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            level TEXT NOT NULL,
            delay_minutes INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            bus_id TEXT,
            severity TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


def reset_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS alerts")
    cursor.execute("DROP TABLE IF EXISTS traffic")
    cursor.execute("DROP TABLE IF EXISTS buses")
    cursor.execute("DROP TABLE IF EXISTS routes")
    cursor.execute("DROP TABLE IF EXISTS stops")

    connection.commit()

    connection.close()

    initialize_database()


def insert_bus(bus):

    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO buses
        (
            id,
            registration,
            route_id,
            capacity,
            passengers,
            latitude,
            longitude,
            speed,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bus["id"],
        bus["registration"],
        bus["route_id"],
        bus["capacity"],
        bus["passengers"],
        bus["latitude"],
        bus["longitude"],
        bus["speed"],
        bus["status"]
    ))

    connection.commit()

    connection.close()


def insert_route(route):

    connection = get_connection()

    stops = ",".join(
        route["stops"]
    )

    connection.execute("""
        INSERT OR REPLACE INTO routes
        (
            id,
            name,
            source,
            destination,
            stops
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        route["id"],
        route["name"],
        route["source"],
        route["destination"],
        stops
    ))

    connection.commit()

    connection.close()


def insert_stop(stop):

    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO stops
        (
            id,
            name,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?)
    """, (
        stop["id"],
        stop["name"],
        stop["latitude"],
        stop["longitude"]
    ))

    connection.commit()

    connection.close()


def insert_traffic(item):

    connection = get_connection()

    connection.execute("""
        INSERT INTO traffic
        (
            location,
            level,
            delay_minutes
        )
        VALUES (?, ?, ?)
    """, (
        item["location"],
        item["level"],
        item["delay_minutes"]
    ))

    connection.commit()

    connection.close()


def get_all_buses():

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM buses"
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_bus(bus_id):

    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM buses WHERE id = ?",
        (bus_id,)
    ).fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def get_all_routes():

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM routes"
    ).fetchall()

    connection.close()

    routes = []

    for row in rows:

        route = dict(row)

        route["stops"] = (
            route["stops"].split(",")
            if route["stops"]
            else []
        )

        routes.append(route)

    return routes


def get_route(route_id):

    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM routes WHERE id = ?",
        (route_id,)
    ).fetchone()

    connection.close()

    if not row:
        return None

    route = dict(row)

    route["stops"] = (
        route["stops"].split(",")
        if route["stops"]
        else []
    )

    return route


def get_all_stops():

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM stops"
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_stop(stop_id):

    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM stops WHERE id = ?",
        (stop_id,)
    ).fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def get_traffic():

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM traffic"
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_alerts():

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM alerts ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def create_alert(
    alert_type,
    message,
    bus_id,
    severity
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO alerts
        (
            type,
            message,
            bus_id,
            severity
        )
        VALUES (?, ?, ?, ?)
    """, (
        alert_type,
        message,
        bus_id,
        severity
    ))

    connection.commit()

    connection.close()


def update_bus_location(
    bus_id,
    latitude,
    longitude,
    speed
):

    connection = get_connection()

    connection.execute("""
        UPDATE buses
        SET latitude = ?,
            longitude = ?,
            speed = ?
        WHERE id = ?
    """, (
        latitude,
        longitude,
        speed,
        bus_id
    ))

    connection.commit()

    connection.close()


def update_bus_status(
    bus_id,
    status
):

    connection = get_connection()

    connection.execute("""
        UPDATE buses
        SET status = ?
        WHERE id = ?
    """, (
        status,
        bus_id
    ))

    connection.commit()

    connection.close()


def update_passengers(
    bus_id,
    passengers
):

    connection = get_connection()

    connection.execute("""
        UPDATE buses
        SET passengers = ?
        WHERE id = ?
    """, (
        passengers,
        bus_id
    ))

    connection.commit()

    connection.close()