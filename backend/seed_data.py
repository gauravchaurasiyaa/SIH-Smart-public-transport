from database import (
    reset_database,
    insert_bus,
    insert_route,
    insert_stop,
    insert_traffic
)

from transport_data import (
    BUSES,
    ROUTES,
    STOPS,
    TRAFFIC
)


def seed_database():

    print("Resetting database...")

    reset_database()

    print("Adding routes...")

    for route in ROUTES:
        insert_route(route)

    print("Adding stops...")

    for stop in STOPS:
        insert_stop(stop)

    print("Adding buses...")

    for bus in BUSES:
        insert_bus(bus)

    print("Adding traffic data...")

    for traffic in TRAFFIC:
        insert_traffic(traffic)

    print("")
    print("================================")
    print("SMART BUS DATABASE READY")
    print("================================")
    print(f"Routes: {len(ROUTES)}")
    print(f"Stops: {len(STOPS)}")
    print(f"Buses: {len(BUSES)}")
    print(f"Traffic zones: {len(TRAFFIC)}")
    print("================================")


if __name__ == "__main__":
    seed_database()