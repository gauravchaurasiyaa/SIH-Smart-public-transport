from database import get_connection


def add_routes():

    connection = get_connection()
    cursor = connection.cursor()

    routes = [
        (
            "R102",
            "College - Railway Station",
            "College",
            "Railway Station",
            8.5
        ),
        (
            "R205",
            "University - City Center",
            "University",
            "City Center",
            6.2
        ),
        (
            "R310",
            "Airport - Railway Station",
            "Airport Road",
            "Railway Station",
            12.4
        )
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO routes (
            route_number,
            route_name,
            start_point,
            end_point,
            total_distance
        )
        VALUES (?, ?, ?, ?, ?)
    """, routes)

    connection.commit()
    connection.close()

    print("Routes added successfully.")


def add_bus_stops():

    connection = get_connection()
    cursor = connection.cursor()

    stops = [
        ("College", "College", 26.8467, 80.9462),
        ("Main Market", "Main Market", 26.8480, 80.9500),
        ("Central Mall", "Central Mall", 26.8505, 80.9550),
        ("Railway Station", "Railway Station", 26.8320, 80.9180),
        ("University", "University", 26.8465, 80.9390),
        ("City Center", "City Center", 26.8550, 80.9490),
        ("Airport Road", "Airport Road", 26.7606, 80.8893),
        ("Bus Terminal", "Bus Terminal", 26.8380, 80.9340)
    ]

    cursor.executemany("""
        INSERT INTO bus_stops (
            stop_name,
            location,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?)
    """, stops)

    connection.commit()
    connection.close()

    print("Bus stops added successfully.")


def connect_route_stops():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT id, route_number
        FROM routes
    """)

    routes = cursor.fetchall()


    cursor.execute("""
        SELECT id, stop_name
        FROM bus_stops
    """)

    stops = cursor.fetchall()


    route_ids = {}

    for route in routes:
        route_ids[route["route_number"]] = route["id"]


    stop_ids = {}

    for stop in stops:
        stop_ids[stop["stop_name"]] = stop["id"]


    route_stop_data = [

        (
            route_ids["R102"],
            stop_ids["College"],
            1
        ),

        (
            route_ids["R102"],
            stop_ids["Main Market"],
            2
        ),

        (
            route_ids["R102"],
            stop_ids["Central Mall"],
            3
        ),

        (
            route_ids["R102"],
            stop_ids["Railway Station"],
            4
        ),

        (
            route_ids["R205"],
            stop_ids["University"],
            1
        ),

        (
            route_ids["R205"],
            stop_ids["City Center"],
            2
        ),

        (
            route_ids["R310"],
            stop_ids["Airport Road"],
            1
        ),

        (
            route_ids["R310"],
            stop_ids["Bus Terminal"],
            2
        ),

        (
            route_ids["R310"],
            stop_ids["Railway Station"],
            3
        )
    ]


    cursor.executemany("""
        INSERT INTO route_stops (
            route_id,
            stop_id,
            stop_order
        )
        VALUES (?, ?, ?)
    """, route_stop_data)


    connection.commit()
    connection.close()

    print("Route stops connected successfully.")


def add_buses():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT id, route_number, route_name
        FROM routes
    """)

    routes = cursor.fetchall()


    route_ids = {}

    for route in routes:

        route_ids[route["route_number"]] = {
            "id": route["id"],
            "name": route["route_name"]
        }


    buses = [
        (
            "102",
            route_ids["R102"]["id"],
            route_ids["R102"]["name"],
            "College",
            "Main Market",
            8,
            76,
            "Running"
        ),

        (
            "205",
            route_ids["R205"]["id"],
            route_ids["R205"]["name"],
            "University",
            "City Center",
            12,
            52,
            "Running"
        ),

        (
            "310",
            route_ids["R310"]["id"],
            route_ids["R310"]["name"],
            "Airport Road",
            "Bus Terminal",
            18,
            34,
            "Running"
        )
    ]


    cursor.executemany("""
        INSERT INTO buses (
            bus_number,
            route_id,
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
    connection.close()

    print("Buses added successfully.")


if __name__ == "__main__":

    add_routes()

    add_bus_stops()

    connect_route_stops()

    add_buses()

    print("Complete transport data added successfully.")