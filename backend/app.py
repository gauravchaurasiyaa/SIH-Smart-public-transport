from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# =========================
# SAMPLE BUS DATA
# =========================

buses = [
    {
        "number": "SB-101",
        "route": "City Center → University",
        "location": "Main Road",
        "nextStop": "University Gate",
        "eta": 6,
        "crowd": 28,
        "fare": 20,
        "status": "On time"
    },
    {
        "number": "SB-204",
        "route": "Railway Station → University",
        "location": "MG Road",
        "nextStop": "College Road",
        "eta": 10,
        "crowd": 46,
        "fare": 25,
        "status": "On time"
    },
    {
        "number": "SB-315",
        "route": "Bus Stand → City Center",
        "location": "Civil Lines",
        "nextStop": "City Mall",
        "eta": 14,
        "crowd": 72,
        "fare": 20,
        "status": "Busy"
    },
    {
        "number": "SB-408",
        "route": "Airport → City Center",
        "location": "Airport Road",
        "nextStop": "Metro Point",
        "eta": 18,
        "crowd": 35,
        "fare": 30,
        "status": "On time"
    }
]


# =========================
# TRAVEL HISTORY
# =========================

travel_history = [
    {
        "bus": "SB-101",
        "route": "City Center → University",
        "fare": 20,
        "date": "Today"
    },
    {
        "bus": "SB-204",
        "route": "Railway Station → University",
        "fare": 25,
        "date": "Yesterday"
    },
    {
        "bus": "SB-101",
        "route": "University → City Center",
        "fare": 20,
        "date": "2 days ago"
    },
    {
        "bus": "SB-315",
        "route": "Bus Stand → City Center",
        "fare": 20,
        "date": "3 days ago"
    }
]


# =========================
# HOME / HEALTH CHECK
# =========================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Smart Bus API is running"
    })


# =========================
# GET ALL BUSES
# =========================

@app.route("/api/buses", methods=["GET"])
def get_buses():
    return jsonify(buses)


# =========================
# GET SINGLE BUS
# =========================

@app.route("/api/buses/<bus_number>", methods=["GET"])
def get_bus(bus_number):

    for bus in buses:

        if bus["number"].lower() == bus_number.lower():
            return jsonify(bus)

    return jsonify({
        "error": "Bus not found"
    }), 404


# =========================
# SEARCH ROUTE
# =========================

@app.route("/api/search", methods=["GET"])
def search_route():

    from_location = request.args.get(
        "from",
        ""
    ).strip()

    to_location = request.args.get(
        "to",
        ""
    ).strip()

    if not from_location or not to_location:

        return jsonify({
            "error": "Both from and to are required"
        }), 400


    sorted_buses = sorted(
        buses,
        key=lambda bus:
        bus["eta"] + bus["crowd"] / 10
    )


    return jsonify({
        "from": from_location,
        "to": to_location,
        "recommended": sorted_buses[0],
        "buses": sorted_buses
    })


# =========================
# AI RECOMMENDATION
# =========================

@app.route("/api/recommend", methods=["GET"])
def recommend_bus():

    recommended = min(
        buses,
        key=lambda bus:
        bus["eta"] + bus["crowd"] / 10
    )

    return jsonify({
        "recommended": recommended,
        "reason": (
            "Best balance between ETA "
            "and crowd level."
        )
    })


# =========================
# LOWEST CROWD BUS
# =========================

@app.route("/api/lowest-crowd", methods=["GET"])
def lowest_crowd():

    bus = min(
        buses,
        key=lambda item: item["crowd"]
    )

    return jsonify(bus)


# =========================
# FASTEST BUS
# =========================

@app.route("/api/fastest", methods=["GET"])
def fastest_bus():

    bus = min(
        buses,
        key=lambda item: item["eta"]
    )

    return jsonify(bus)


# =========================
# TRAVEL HISTORY
# =========================

@app.route("/api/history", methods=["GET"])
def get_history():

    return jsonify(travel_history)


# =========================
# EXPENSES
# =========================

@app.route("/api/expenses", methods=["GET"])
def get_expenses():

    total = sum(
        item["fare"]
        for item in travel_history
    )

    trips = len(travel_history)

    average = (
        round(total / trips)
        if trips
        else 0
    )

    return jsonify({
        "weekly": total,
        "monthly": total,
        "average": average,
        "trips": trips
    })


# =========================
# ADD TRAVEL RECORD
# =========================

@app.route("/api/history", methods=["POST"])
def add_history():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400


    required = [
        "bus",
        "route",
        "fare"
    ]

    for field in required:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400


    record = {
        "bus": data["bus"],
        "route": data["route"],
        "fare": data["fare"],
        "date": data.get(
            "date",
            "Today"
        )
    }

    travel_history.insert(
        0,
        record
    )

    return jsonify({
        "message": "Travel record added",
        "record": record
    }), 201


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )