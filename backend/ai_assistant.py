import sqlite3
import os


DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "transport.db"
)


def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def get_bus_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            bus_number,
            route_id,
            route_name,
            current_location,
            next_stop,
            eta,
            occupancy,
            status
        FROM buses
    """)

    buses = cursor.fetchall()

    connection.close()

    return buses


def get_expense_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(fare), 0) AS total_expense,
            COUNT(*) AS total_trips
        FROM bus_expenses
    """)

    result = cursor.fetchone()

    connection.close()

    return result


def get_route_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            route_number,
            route_name,
            start_point,
            end_point,
            total_distance
        FROM routes
    """)

    routes = cursor.fetchall()

    connection.close()

    return routes


def generate_response(question):

    question = question.lower().strip()

    buses = get_bus_data()

    expense = get_expense_data()

    routes = get_route_data()


    if not buses:

        return {
            "success": True,
            "response": "I don't have any bus data available right now."
        }


    # =====================================
    # LEAST CROWDED BUS
    # =====================================

    if (
        "least crowded" in question
        or "less crowded" in question
        or "low crowd" in question
        or "less people" in question
        or "empty bus" in question
    ):

        best_bus = min(
            buses,
            key=lambda bus: bus["occupancy"]
        )

        return {
            "success": True,
            "response": (
                f"Bus {best_bus['bus_number']} "
                f"has the lowest crowd level at "
                f"{best_bus['occupancy']}%. "
                f"It is currently near "
                f"{best_bus['current_location']}."
            )
        }


    # =====================================
    # FASTEST BUS
    # =====================================

    if (
        "fastest" in question
        or "quickest" in question
        or "fast bus" in question
    ):

        best_bus = min(
            buses,
            key=lambda bus: bus["eta"]
        )

        return {
            "success": True,
            "response": (
                f"Bus {best_bus['bus_number']} "
                f"is currently the fastest option. "
                f"Its ETA is approximately "
                f"{best_bus['eta']} minutes."
            )
        }


    # =====================================
    # ETA
    # =====================================

    if (
        "eta" in question
        or "arrival" in question
        or "arrive" in question
        or "how long" in question
    ):

        best_bus = min(
            buses,
            key=lambda bus: bus["eta"]
        )

        return {
            "success": True,
            "response": (
                f"The quickest available bus is "
                f"{best_bus['bus_number']}. "
                f"It should arrive in about "
                f"{best_bus['eta']} minutes."
            )
        }


    # =====================================
    # EXPENSE
    # =====================================

    if (
        "expense" in question
        or "spending" in question
        or "spend" in question
        or "spent" in question
        or "money" in question
        or "bus cost" in question
    ):

        return {
            "success": True,
            "response": (
                f"You have recorded ₹"
                f"{expense['total_expense']:.0f} "
                f"of bus travel expenses across "
                f"{expense['total_trips']} trips."
            )
        }


    # =====================================
    # BUS STATUS
    # =====================================

    if (
        "status" in question
        or "running" in question
        or "active bus" in question
    ):

        active_buses = [
            bus for bus in buses
            if str(bus["status"]).lower()
            in ["active", "running", "on time"]
        ]

        return {
            "success": True,
            "response": (
                f"There are currently "
                f"{len(active_buses)} active buses "
                f"available in the system."
            )
        }


    # =====================================
    # NEXT STOP
    # =====================================

    if (
        "next stop" in question
        or "next station" in question
        or "where is bus" in question
    ):

        best_bus = min(
            buses,
            key=lambda bus: bus["eta"]
        )

        return {
            "success": True,
            "response": (
                f"Bus {best_bus['bus_number']} "
                f"is currently near "
                f"{best_bus['current_location']} "
                f"and its next stop is "
                f"{best_bus['next_stop']}."
            )
        }


    # =====================================
    # BUS NUMBER
    # =====================================

    for bus in buses:

        bus_number = str(
            bus["bus_number"]
        ).lower()

        if bus_number in question:

            return {
                "success": True,
                "response": (
                    f"Bus {bus['bus_number']} "
                    f"is currently at "
                    f"{bus['current_location']}. "
                    f"Its next stop is "
                    f"{bus['next_stop']}, "
                    f"with an ETA of "
                    f"{bus['eta']} minutes. "
                    f"Current occupancy is "
                    f"{bus['occupancy']}%."
                )
            }


    # =====================================
    # ROUTE INFORMATION
    # =====================================

    for route in routes:

        route_number = str(
            route["route_number"]
        ).lower()

        if route_number in question:

            return {
                "success": True,
                "response": (
                    f"Route {route['route_number']} "
                    f"({route['route_name']}) runs from "
                    f"{route['start_point']} to "
                    f"{route['end_point']} "
                    f"and covers approximately "
                    f"{route['total_distance']} km."
                )
            }


    # =====================================
    # BEST BUS
    # =====================================

    if (
        "best bus" in question
        or "which bus" in question
        or "recommend" in question
        or "suggest" in question
    ):

        best_bus = min(
            buses,
            key=lambda bus: (
                bus["eta"] +
                bus["occupancy"] / 10
            )
        )

        return {
            "success": True,
            "response": (
                f"I recommend bus "
                f"{best_bus['bus_number']}. "
                f"It has an ETA of "
                f"{best_bus['eta']} minutes "
                f"and occupancy of "
                f"{best_bus['occupancy']}%."
            )
        }


    # =====================================
    # HELP
    # =====================================

    if (
        "help" in question
        or "what can you do" in question
    ):

        return {
            "success": True,
            "response": (
                "I can help you find the fastest "
                "or least crowded bus, check ETA, "
                "bus status, next stops, route details, "
                "and analyse your bus travel expenses."
            )
        }


    # =====================================
    # DEFAULT
    # =====================================

    return {
        "success": True,
        "response": (
            "I can help with bus routes, ETA, "
            "crowd levels, bus status and expenses. "
            "Try asking: Which bus is least crowded?"
        )
    }