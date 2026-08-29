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
            "Central Mall",
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

    add_buses()

    print("Transport data added successfully.")