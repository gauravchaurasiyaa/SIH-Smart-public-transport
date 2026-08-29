from database import get_connection


connection = get_connection()
cursor = connection.cursor()


# =========================
# REMOVE ALL OLD DEMO DATA
# =========================

cursor.execute("""
    DELETE FROM buses
""")


cursor.execute("""
    DELETE FROM route_stops
""")


cursor.execute("""
    DELETE FROM routes
""")


# =========================
# REALISTIC ROUTES
# =========================

routes = [

    (
        "NH24",
        "NH24 City Express",
        "College",
        "Railway Station",
        6.5
    ),

    (
        "NH28",
        "NH28 City Local",
        "College",
        "Railway Station",
        8.2
    ),

    (
        "NH91",
        "NH91 Fast Service",
        "College",
        "Railway Station",
        5.8
    )

]


for route in routes:

    cursor.execute("""
        INSERT INTO routes
        (
            route_number,
            route_name,
            start_point,
            end_point,
            total_distance
        )
        VALUES (?, ?, ?, ?, ?)
    """, route)


# =========================
# GET ROUTE IDs
# =========================

cursor.execute("""
    SELECT
        id,
        route_number
    FROM routes
""")


route_rows = cursor.fetchall()


route_ids = {}

for route in route_rows:

    route_ids[route["route_number"]] = route["id"]


# =========================
# REALISTIC BUS DATA
# =========================

buses = [

    (
        "UP 53 NC 0007",
        route_ids["NH24"],
        "NH24 City Express",
        "College",
        "Main Market",
        8,
        42,
        "Running"
    ),

    (
        "UP 53 NC 0001",
        route_ids["NH24"],
        "NH24 City Express",
        "University Gate",
        "College",
        14,
        58,
        "Running"
    ),

    (
        "UP 53 NC 7861",
        route_ids["NH28"],
        "NH28 City Local",
        "College",
        "City Mall",
        12,
        28,
        "Running"
    ),

    (
        "UP 53 NC 9999",
        route_ids["NH28"],
        "NH28 City Local",
        "Library Road",
        "College",
        18,
        35,
        "Running"
    ),

    (
        "UP 53 NC 1111",
        route_ids["NH91"],
        "NH91 Fast Service",
        "College",
        "Central Market",
        5,
        92,
        "Running"
    ),

    (
        "UP 53 NC 0009",
        route_ids["NH91"],
        "NH91 Fast Service",
        "Bus Stand",
        "College",
        10,
        76,
        "Delayed"
    )

]


for bus in buses:

    cursor.execute("""
        INSERT INTO buses
        (
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
    """, bus)


connection.commit()

connection.close()


print("All old route data removed.")
print("New NH24, NH28 and NH91 bus data added successfully.")