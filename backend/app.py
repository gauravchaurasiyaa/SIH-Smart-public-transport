from flask import Flask, jsonify, request, send_from_directory, render_template, session, redirect
from flask_cors import CORS
import sqlite3
import os
import random
import math
from datetime import datetime 

# ============================================================
# SMART BUS BACKEND — STEP 4
# Real-time simulation + Smart Recommendation Engine
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
DATABASE_DIR = os.path.join(PROJECT_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "transport.db")

os.makedirs(DATABASE_DIR, exist_ok=True)

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
CORS (app)



app.secret_key = "smart-bus-secret-key"

CORS(app)


@app.route("/login", methods=["GET", "POST"])
def login():

    

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template(
                "login.html",
                error="Please enter email and password."
            )

        session["logged_in"] = True
        session["email"] = email

        return redirect("/")

    return render_template("login.html")



@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
        
# ============================================================
# BUS DATA
# ============================================================

BUS_DATA = [
    {
        "id": 1,
        "registration": "UP53NC0001",
        "route_id": 1,
        "capacity": 50,
        "passengers": 18,
        "latitude": 28.6692,
        "longitude": 77.4538,
        "speed": 38,
        "status": "On Route",
        "route": "NH24",
        "location": "Ghaziabad",
        "next_stop": "Hapur Road",
        "eta": 6,
        "fare": 25,
        "manufacturing_year": 2023,
        "bus_age": 3,
        "condition": "Excellent",
        "fitness_status": "Valid",
        "fitness_expiry": "31/12/2027",
        "permit_status": "Valid",
        "permit_expiry": "30/06/2027",
        "insurance_status": "Valid",
        "insurance_expiry": "15/09/2027",
        "last_inspection": "12/08/2026",
        "safety_score": 96,
        "driver_name": "Rajesh Kumar",
        "driver_experience": "12 years",
        "driver_rating": 4.8,
        "conductor_name": "Amit Singh",
        "conductor_experience": "7 years",
        "conductor_rating": 4.6
    },
    {
        "id": 2,
        "registration": "UP53NC0002",
        "route_id": 1,
        "capacity": 50,
        "passengers": 31,
        "latitude": 28.6815,
        "longitude": 77.4442,
        "speed": 29,
        "status": "On Route",
        "route": "NH24",
        "location": "Dasna",
        "next_stop": "Masuri",
        "eta": 10,
        "fare": 30,
        "manufacturing_year": 2021,
        "bus_age": 5,
        "condition": "Good",
        "fitness_status": "Valid",
        "fitness_expiry": "30/11/2026",
        "permit_status": "Valid",
        "permit_expiry": "31/03/2027",
        "insurance_status": "Valid",
        "insurance_expiry": "21/11/2026",
        "last_inspection": "05/08/2026",
        "safety_score": 91,
        "driver_name": "Vijay Sharma",
        "driver_experience": "9 years",
        "driver_rating": 4.7,
        "conductor_name": "Suresh Yadav",
        "conductor_experience": "6 years",
        "conductor_rating": 4.5
    },
    {
        "id": 3,
        "registration": "UP53NC0003",
        "route_id": 2,
        "capacity": 50,
        "passengers": 22,
        "latitude": 26.7589,
        "longitude": 83.2155,
        "speed": 42,
        "status": "On Time",
        "route": "NH28",
        "location": "Sahjanwa",
        "next_stop": "Basti",
        "eta": 8,
        "fare": 35,
        "manufacturing_year": 2024,
        "bus_age": 2,
        "condition": "Excellent",
        "fitness_status": "Valid",
        "fitness_expiry": "31/12/2028",
        "permit_status": "Valid",
        "permit_expiry": "31/08/2028",
        "insurance_status": "Valid",
        "insurance_expiry": "18/12/2027",
        "last_inspection": "18/08/2026",
        "safety_score": 98,
        "driver_name": "Manoj Verma",
        "driver_experience": "15 years",
        "driver_rating": 4.9,
        "conductor_name": "Deepak Mishra",
        "conductor_experience": "10 years",
        "conductor_rating": 4.8
    },
    {
        "id": 4,
        "registration": "UP53NC0004",
        "route_id": 2,
        "capacity": 50,
        "passengers": 37,
        "latitude": 26.8067,
        "longitude": 82.7235,
        "speed": 25,
        "status": "Delayed",
        "route": "NH28",
        "location": "Basti",
        "next_stop": "Ayodhya",
        "eta": 17,
        "fare": 40,
        "manufacturing_year": 2019,
        "bus_age": 7,
        "condition": "Good",
        "fitness_status": "Valid",
        "fitness_expiry": "30/09/2026",
        "permit_status": "Valid",
        "permit_expiry": "31/01/2027",
        "insurance_status": "Valid",
        "insurance_expiry": "05/10/2026",
        "last_inspection": "01/08/2026",
        "safety_score": 87,
        "driver_name": "Anil Gupta",
        "driver_experience": "11 years",
        "driver_rating": 4.5,
        "conductor_name": "Rohit Kumar",
        "conductor_experience": "5 years",
        "conductor_rating": 4.3
    },
    {
        "id": 5,
        "registration": "UP53NC0005",
        "route_id": 3,
        "capacity": 52,
        "passengers": 20,
        "latitude": 26.2345,
        "longitude": 81.2409,
        "speed": 40,
        "status": "On Route",
        "route": "NH30",
        "location": "Raebareli",
        "next_stop": "Prayagraj",
        "eta": 11,
        "fare": 30,
        "manufacturing_year": 2022,
        "bus_age": 4,
        "condition": "Excellent",
        "fitness_status": "Valid",
        "fitness_expiry": "31/10/2027",
        "permit_status": "Valid",
        "permit_expiry": "30/04/2027",
        "insurance_status": "Valid",
        "insurance_expiry": "12/07/2027",
        "last_inspection": "10/08/2026",
        "safety_score": 94,
        "driver_name": "Sanjay Patel",
        "driver_experience": "13 years",
        "driver_rating": 4.8,
        "conductor_name": "Pankaj Singh",
        "conductor_experience": "8 years",
        "conductor_rating": 4.7
    },
    {
        "id": 6,
        "registration": "UP53NC0006",
        "route_id": 3,
        "capacity": 52,
        "passengers": 43,
        "latitude": 25.4277,
        "longitude": 86.1292,
        "speed": 22,
        "status": "Delayed",
        "route": "NH30",
        "location": "Barauni",
        "next_stop": "Patna",
        "eta": 19,
        "fare": 45,
        "manufacturing_year": 2018,
        "bus_age": 8,
        "condition": "Fair",
        "fitness_status": "Valid",
        "fitness_expiry": "31/10/2026",
        "permit_status": "Valid",
        "permit_expiry": "30/12/2026",
        "insurance_status": "Valid",
        "insurance_expiry": "20/10/2026",
        "last_inspection": "28/07/2026",
        "safety_score": 82,
        "driver_name": "Ramesh Singh",
        "driver_experience": "17 years",
        "driver_rating": 4.4,
        "conductor_name": "Kamal Kumar",
        "conductor_experience": "9 years",
        "conductor_rating": 4.4
    },
    {
        "id": 7,
        "registration": "UP53NC0007",
        "route_id": 4,
        "capacity": 50,
        "passengers": 14,
        "latitude": 26.7352,
        "longitude": 83.3918,
        "speed": 44,
        "status": "On Time",
        "route": "NH27",
        "location": "Gorakhpur Bypass",
        "next_stop": "Kasia",
        "eta": 7,
        "fare": 25,
        "manufacturing_year": 2024,
        "bus_age": 2,
        "condition": "Excellent",
        "fitness_status": "Valid",
        "fitness_expiry": "31/12/2028",
        "permit_status": "Valid",
        "permit_expiry": "31/05/2028",
        "insurance_status": "Valid",
        "insurance_expiry": "25/12/2027",
        "last_inspection": "20/08/2026",
        "safety_score": 99,
        "driver_name": "Arjun Tiwari",
        "driver_experience": "10 years",
        "driver_rating": 4.9,
        "conductor_name": "Naveen Sharma",
        "conductor_experience": "6 years",
        "conductor_rating": 4.8
    },
    {
        "id": 8,
        "registration": "UP53NC0008",
        "route_id": 4,
        "capacity": 50,
        "passengers": 28,
        "latitude": 26.7439,
        "longitude": 83.8882,
        "speed": 34,
        "status": "On Route",
        "route": "NH27",
        "location": "Kasia",
        "next_stop": "Kushinagar",
        "eta": 12,
        "fare": 35,
        "manufacturing_year": 2020,
        "bus_age": 6,
        "condition": "Good",
        "fitness_status": "Valid",
        "fitness_expiry": "31/08/2027",
        "permit_status": "Valid",
        "permit_expiry": "31/03/2027",
        "insurance_status": "Valid",
        "insurance_expiry": "14/09/2027",
        "last_inspection": "08/08/2026",
        "safety_score": 89,
        "driver_name": "Dinesh Yadav",
        "driver_experience": "14 years",
        "driver_rating": 4.6,
        "conductor_name": "Mukesh Verma",
        "conductor_experience": "7 years",
        "conductor_rating": 4.5
    }
]

# ============================================================
# ROUTES
# ============================================================

ROUTE_DATA = [
    {
        "id": 1,
        "name": "NH24",
        "source": "Ghaziabad",
        "destination": "Hapur",
        "stops": "Ghaziabad,Hapur Road,Dasna,Masuri,Hapur"
    },
    {
        "id": 2,
        "name": "NH28",
        "source": "Gorakhpur",
        "destination": "Lucknow",
        "stops": "Gorakhpur,Sahjanwa,Basti,Ayodhya,Lucknow"
    },
    {
        "id": 3,
        "name": "NH30",
        "source": "Lucknow",
        "destination": "Patna",
        "stops": "Lucknow,Raebareli,Prayagraj,Barauni,Patna"
    },
    {
        "id": 4,
        "name": "NH27",
        "source": "Gorakhpur",
        "destination": "Kushinagar",
        "stops": "Gorakhpur,Gorakhpur Bypass,Kasia,Kushinagar"
    }
]

# ============================================================
# STOPS
# ============================================================

STOP_DATA = [
    ("Ghaziabad", 28.6692, 77.4538),
    ("Hapur Road", 28.6754, 77.4511),
    ("Dasna", 28.6815, 77.4442),
    ("Masuri", 28.6942, 77.4381),
    ("Hapur", 28.7301, 77.7757),

    ("Gorakhpur", 26.7606, 83.3732),
    ("Sahjanwa", 26.7589, 83.2155),
    ("Basti", 26.8067, 82.7235),
    ("Ayodhya", 26.7922, 82.1998),
    ("Lucknow", 26.8467, 80.9462),

    ("Raebareli", 26.2345, 81.2409),
    ("Prayagraj", 25.4358, 81.8463),
    ("Barauni", 25.4277, 86.1292),
    ("Patna", 25.5941, 85.1376),

    ("Gorakhpur Bypass", 26.7352, 83.3918),
    ("Kasia", 26.7439, 83.8882),
    ("Kushinagar", 26.7397, 83.8888)
]

# ============================================================
# TRAFFIC
# ============================================================

TRAFFIC_DATA = [
    {
        "id": 1,
        "location": "Dasna",
        "level": "Moderate",
        "delay_minutes": 4
    },
    {
        "id": 2,
        "location": "Hapur Road",
        "level": "Low",
        "delay_minutes": 1
    },
    {
        "id": 3,
        "location": "Basti",
        "level": "High",
        "delay_minutes": 8
    },
    {
        "id": 4,
        "location": "Raebareli",
        "level": "Moderate",
        "delay_minutes": 5
    },
    {
        "id": 5,
        "location": "Gorakhpur Bypass",
        "level": "Low",
        "delay_minutes": 2
    }
]

# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# REAL-TIME BUS SIMULATION
# ============================================================

STOP_COORDINATES = {
    stop[0]: {
        "latitude": stop[1],
        "longitude": stop[2]
    }
    for stop in STOP_DATA
}

SIMULATION_STATE = {}

for bus in BUS_DATA:
    SIMULATION_STATE[bus["id"]] = {
        "latitude": bus["latitude"],
        "longitude": bus["longitude"],
        "stop_index": 0,
        "last_update": datetime.now()
    }


def distance_km(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


def get_route_stop_names(bus):

    for route in ROUTE_DATA:

        if route["id"] == bus["route_id"]:
            return [
                stop.strip()
                for stop in route["stops"].split(",")
            ]

    return []


def initialize_simulation(bus):

    stops = get_route_stop_names(bus)

    if not stops:
        return

    closest_index = 0
    closest_distance = float("inf")

    for index, stop_name in enumerate(stops):

        coordinates = STOP_COORDINATES.get(stop_name)

        if not coordinates:
            continue

        distance = distance_km(
            bus["latitude"],
            bus["longitude"],
            coordinates["latitude"],
            coordinates["longitude"]
        )

        if distance < closest_distance:

            closest_distance = distance
            closest_index = index

    SIMULATION_STATE[
        bus["id"]
    ]["stop_index"] = closest_index


for bus in BUS_DATA:
    initialize_simulation(bus)


def simulate_bus(bus):

    state = SIMULATION_STATE[bus["id"]]

    stops = get_route_stop_names(bus)

    if len(stops) < 2:
        return bus

    current_index = state["stop_index"]

    if current_index >= len(stops) - 1:

        current_index = 0
        state["stop_index"] = 0

    next_index = current_index + 1

    current_stop_name = stops[current_index]
    next_stop_name = stops[next_index]

    current_stop = STOP_COORDINATES.get(
        current_stop_name
    )

    next_stop = STOP_COORDINATES.get(
        next_stop_name
    )

    if not current_stop or not next_stop:
        return bus

    latitude = state["latitude"]
    longitude = state["longitude"]

    target_latitude = next_stop["latitude"]
    target_longitude = next_stop["longitude"]

    remaining_distance = distance_km(
        latitude,
        longitude,
        target_latitude,
        target_longitude
    )

    movement_factor = 0.08

    if bus["status"].lower() == "delayed":
        movement_factor = 0.045

    if bus["speed"] >= 40:
        movement_factor += 0.025

    elif bus["speed"] <= 25:
        movement_factor -= 0.015

    movement_factor = max(
        0.025,
        min(0.15, movement_factor)
    )

    new_latitude = latitude + (
        target_latitude - latitude
    ) * movement_factor

    new_longitude = longitude + (
        target_longitude - longitude
    ) * movement_factor

    if remaining_distance < 0.7:

        state["latitude"] = target_latitude
        state["longitude"] = target_longitude

        state["stop_index"] = next_index

        bus["location"] = next_stop_name

        if next_index >= len(stops) - 1:

            state["stop_index"] = 0
            bus["next_stop"] = stops[0]

        else:

            bus["next_stop"] = stops[
                next_index + 1
            ]

        bus["eta"] = random.randint(4, 10)

    else:

        state["latitude"] = new_latitude
        state["longitude"] = new_longitude

        bus["location"] = current_stop_name
        bus["next_stop"] = next_stop_name

        effective_speed = max(
            bus["speed"],
            15
        )

        calculated_eta = (
            remaining_distance / effective_speed
        ) * 60

        bus["eta"] = max(
            1,
            round(calculated_eta)
        )

    original_speed = bus["speed"]

    speed_change = random.choice([
        -3,
        -2,
        -1,
        0,
        0,
        1,
        2,
        3
    ])

    new_speed = original_speed + speed_change

    if bus["status"] == "Delayed":
        new_speed = min(
            new_speed,
            32
        )

    new_speed = max(
        15,
        min(60, new_speed)
    )

    bus["speed"] = new_speed

    passenger_change = random.choice([
        -2,
        -1,
        0,
        0,
        1,
        2
    ])

    new_passengers = (
        bus["passengers"]
        + passenger_change
    )

    new_passengers = max(
        5,
        min(
            bus["capacity"],
            new_passengers
        )
    )

    bus["passengers"] = new_passengers

    crowd_percent = (
        new_passengers
        / bus["capacity"]
    ) * 100

    if bus["status"] == "Delayed":

        if random.random() < 0.20:
            bus["status"] = "On Route"

    elif crowd_percent >= 90:

        bus["status"] = "Crowded"

    elif bus["eta"] >= 15:

        bus["status"] = "Delayed"

    elif bus["speed"] >= 40:

        bus["status"] = "On Time"

    else:

        bus["status"] = "On Route"

    state["last_update"] = datetime.now()

    return bus


# ============================================================
# SMART RECOMMENDATION ENGINE
# ============================================================

def get_traffic_delay(bus):

    delay = 0

    for traffic in TRAFFIC_DATA:

        if traffic["location"].lower() in [
            bus["location"].lower(),
            bus["next_stop"].lower()
        ]:

            delay += traffic["delay_minutes"]

    return delay


def calculate_smart_score(bus):

    eta = float(bus["eta"])

    crowd = (
        bus["passengers"]
        / bus["capacity"]
    ) * 100

    safety = float(
        bus["safety_score"]
    )

    fare = float(
        bus["fare"]
    )

    speed = float(
        bus["speed"]
    )

    traffic_delay = get_traffic_delay(bus)

    score = 100

    # --------------------------------------------------------
    # ETA
    # Faster buses receive higher score.
    # --------------------------------------------------------

    eta_score = max(
        0,
        30 - (eta * 1.5)
    )

    score += eta_score

    # --------------------------------------------------------
    # CROWD
    # Less crowded buses receive higher score.
    # --------------------------------------------------------

    crowd_score = max(
        0,
        25 - (crowd * 0.25)
    )

    score += crowd_score

    # --------------------------------------------------------
    # SAFETY
    # Safety is heavily weighted.
    # --------------------------------------------------------

    safety_score = safety * 0.30

    score += safety_score

    # --------------------------------------------------------
    # FARE
    # Lower fare receives a small advantage.
    # --------------------------------------------------------

    fare_score = max(
        0,
        10 - (fare * 0.10)
    )

    score += fare_score

    # --------------------------------------------------------
    # SPEED
    # Higher speed gives a small advantage.
    # --------------------------------------------------------

    speed_score = min(
        8,
        speed * 0.12
    )

    score += speed_score

    # --------------------------------------------------------
    # TRAFFIC
    # Traffic reduces score.
    # --------------------------------------------------------

    traffic_penalty = traffic_delay * 1.5

    score -= traffic_penalty

    # --------------------------------------------------------
    # DELAYED BUS
    # --------------------------------------------------------

    if bus["status"].lower() == "delayed":
        score -= 12

    # --------------------------------------------------------
    # CROWDED BUS
    # --------------------------------------------------------

    if crowd >= 90:
        score -= 15

    elif crowd >= 80:
        score -= 8

    # --------------------------------------------------------
    # Excellent safety bonus
    # --------------------------------------------------------

    if safety >= 95:
        score += 5

    # Keep score within 0-100.
    score = max(
        0,
        min(100, score)
    )

    return round(score, 1)


def get_recommendation_reason(bus):

    reasons = []

    crowd = (
        bus["passengers"]
        / bus["capacity"]
    ) * 100

    traffic_delay = get_traffic_delay(bus)

    if bus["eta"] <= 7:
        reasons.append(
            f"very low ETA ({bus['eta']} min)"
        )

    elif bus["eta"] <= 10:
        reasons.append(
            f"good ETA ({bus['eta']} min)"
        )

    if crowd <= 40:
        reasons.append(
            f"low crowd ({round(crowd)}%)"
        )

    elif crowd <= 60:
        reasons.append(
            f"moderate crowd ({round(crowd)}%)"
        )

    if bus["safety_score"] >= 95:
        reasons.append(
            f"excellent safety score ({bus['safety_score']}/100)"
        )

    elif bus["safety_score"] >= 90:
        reasons.append(
            f"high safety score ({bus['safety_score']}/100)"
        )

    if bus["speed"] >= 40:
        reasons.append(
            f"good speed ({bus['speed']} km/h)"
        )

    if traffic_delay == 0:
        reasons.append(
            "no detected traffic delay"
        )

    elif traffic_delay <= 3:
        reasons.append(
            f"low traffic impact ({traffic_delay} min)"
        )

    if bus["status"].lower() == "delayed":
        reasons.append(
            "currently delayed"
        )

    if not reasons:
        reasons.append(
            "best overall balance of available factors"
        )

    return reasons


def build_smart_recommendation(bus):

    traffic_delay = get_traffic_delay(bus)

    smart_score = calculate_smart_score(
        bus
    )

    reasons = get_recommendation_reason(
        bus
    )

    result = format_bus(bus)

    result["smart_score"] = smart_score

    result["traffic_delay"] = traffic_delay

    result["recommendation_reasons"] = reasons

    result["recommendation"] = (
        "Recommended"
    )

    return result


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def home():

    if not session.get("logged_in"):
        return render_template("login.html")

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    if os.path.exists(index_file):

        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    return jsonify({
        "success": True,
        "project": "SIH Smart Bus",
        "message": "SMART BUS BACKEND IS RUNNING"
    })


@app.route("/<path:path>")
def frontend_files(path):

    requested_file = os.path.join(
        FRONTEND_DIR,
        path
    )

    if os.path.isfile(requested_file):

        return send_from_directory(
            FRONTEND_DIR,
            path
        )

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    if os.path.exists(index_file):

        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    return jsonify({
        "success": False,
        "message": "Frontend file not found"
    }), 404


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "success": True,
        "backend": "online",
        "database": os.path.exists(
            DATABASE_PATH
        ),
        "server_time": datetime.now().isoformat()
    })


# ============================================================
# SYSTEM
# ============================================================

@app.route("/api/system")
def system():

    return jsonify({
        "success": True,
        "project": "SIH Smart Bus",
        "backend": "Flask",
        "database": "SQLite",
        "features": [
            "Smart Bus tracking",
            "Realistic bus locations",
            "Real-time bus simulation",
            "Route information",
            "Stop information",
            "Traffic information",
            "ETA",
            "Crowd level",
            "Bus search",
            "Route search",
            "Live bus demo",
            "Travel history",
            "Travel expense tracking",
            "Smart Bus assistant",
            "Bus safety details",
            "Bus fitness information",
            "Bus permit information",
            "Bus insurance information",
            "Driver information",
            "Conductor information",
            "Safety score",
            "Smart recommendations",
            "Multi-factor recommendation engine",
            "ETA based recommendation",
            "Crowd based recommendation",
            "Safety based recommendation",
            "Traffic aware recommendation",
            "Fare aware recommendation"
        ]
    })


# ============================================================
# FORMAT BUS
# ============================================================

def format_bus(bus):

    crowd = round(
        (
            bus["passengers"]
            / bus["capacity"]
        ) * 100
    )

    return {
        "id": bus["id"],
        "number": bus["registration"],
        "registration": bus["registration"],
        "route": bus["route"],
        "route_id": bus["route_id"],
        "capacity": bus["capacity"],
        "passengers": bus["passengers"],
        "crowd": crowd,
        "occupancy": crowd,
        "occupancy_percent": crowd,
        "latitude": round(
            bus["latitude"],
            6
        ),
        "longitude": round(
            bus["longitude"],
            6
        ),
        "speed": bus["speed"],
        "status": bus["status"],
        "location": bus["location"],
        "current_location": bus["location"],
        "nextStop": bus["next_stop"],
        "next_stop": bus["next_stop"],
        "eta": bus["eta"],
        "eta_minutes": bus["eta"],
        "fare": bus["fare"],
        "manufacturing_year": bus["manufacturing_year"],
        "bus_age": bus["bus_age"],
        "condition": bus["condition"],
        "fitness_status": bus["fitness_status"],
        "fitness_expiry": bus["fitness_expiry"],
        "permit_status": bus["permit_status"],
        "permit_expiry": bus["permit_expiry"],
        "insurance_status": bus["insurance_status"],
        "insurance_expiry": bus["insurance_expiry"],
        "last_inspection": bus["last_inspection"],
        "safety_score": bus["safety_score"],
        "driver": {
            "name": bus["driver_name"],
            "experience": bus["driver_experience"],
            "rating": bus["driver_rating"]
        },
        "conductor": {
            "name": bus["conductor_name"],
            "experience": bus["conductor_experience"],
            "rating": bus["conductor_rating"]
        }
    }


# ============================================================
# BUSES
# ============================================================

@app.route("/api/buses")
def get_buses():

    buses = [
        format_bus(bus)
        for bus in BUS_DATA
    ]

    return jsonify({
        "success": True,
        "count": len(buses),
        "buses": buses
    })


@app.route("/api/buses/<bus_number>")
def get_bus(bus_number):

    for bus in BUS_DATA:

        if (
            bus["registration"].upper()
            == bus_number.upper()
        ):

            return jsonify({
                "success": True,
                "bus": format_bus(bus)
            })

    return jsonify({
        "success": False,
        "message": "Bus not found"
    }), 404


@app.route("/api/buses/<bus_number>/details")
def bus_details(bus_number):

    for bus in BUS_DATA:

        if (
            bus["registration"].upper()
            == bus_number.upper()
        ):

            return jsonify({
                "success": True,
                "bus": format_bus(bus),
                "message": (
                    "Complete bus safety and staff information"
                )
            })

    return jsonify({
        "success": False,
        "message": "Bus not found"
    }), 404


# ============================================================
# LIVE BUSES
# ============================================================

@app.route("/api/live-buses")
def live_buses():

    buses = []

    for original in BUS_DATA:

        bus = dict(original)

        state = SIMULATION_STATE[
            bus["id"]
        ]

        bus["latitude"] = state["latitude"]
        bus["longitude"] = state["longitude"]

        bus = simulate_bus(bus)

        buses.append(
            format_bus(bus)
        )

    return jsonify({
        "success": True,
        "count": len(buses),
        "buses": buses,
        "updated_at": datetime.now().isoformat(),
        "simulation": {
            "enabled": True,
            "mode": "continuous",
            "description": (
                "Simulated real-time bus movement"
            )
        }
    })


# ============================================================
# ROUTES
# ============================================================

@app.route("/api/routes")
def get_routes():

    return jsonify({
        "success": True,
        "count": len(ROUTE_DATA),
        "routes": ROUTE_DATA
    })


@app.route("/api/routes/<route_id>")
def get_route(route_id):

    for route in ROUTE_DATA:

        if (
            str(route["id"])
            == str(route_id)
            or route["name"].upper()
            == route_id.upper()
        ):

            return jsonify({
                "success": True,
                "route": route
            })

    return jsonify({
        "success": False,
        "message": "Route not found"
    }), 404


# ============================================================
# STOPS
# ============================================================

@app.route("/api/stops")
def get_stops():

    stops = [
        {
            "id": i,
            "name": stop[0],
            "latitude": stop[1],
            "longitude": stop[2]
        }
        for i, stop in enumerate(
            STOP_DATA,
            start=1
        )
    ]

    return jsonify({
        "success": True,
        "count": len(stops),
        "stops": stops
    })


@app.route("/api/stops/<stop_id>")
def get_stop(stop_id):

    for index, stop in enumerate(
        STOP_DATA,
        start=1
    ):

        if (
            str(index) == str(stop_id)
            or stop[0].lower()
            == stop_id.lower()
        ):

            return jsonify({
                "success": True,
                "stop": {
                    "id": index,
                    "name": stop[0],
                    "latitude": stop[1],
                    "longitude": stop[2]
                }
            })

    return jsonify({
        "success": False,
        "message": "Stop not found"
    }), 404


# ============================================================
# TRAFFIC
# ============================================================

@app.route("/api/traffic")
def get_traffic():

    return jsonify({
        "success": True,
        "count": len(TRAFFIC_DATA),
        "traffic": TRAFFIC_DATA
    })


# ============================================================
# SEARCH
# ============================================================

@app.route("/api/search")
def search():

    query = request.args.get(
        "q",
        ""
    ).strip().lower()

    if not query:

        return jsonify({
            "success": False,
            "message": (
                "Use /api/search?q=NH24"
            )
        }), 400

    results = []

    for bus in BUS_DATA:

        bus_text = " ".join([
            bus["registration"],
            bus["route"],
            bus["location"],
            bus["next_stop"],
            bus["driver_name"],
            bus["conductor_name"]
        ]).lower()

        if query in bus_text:

            results.append({
                "type": "bus",
                "data": format_bus(bus)
            })

    for route in ROUTE_DATA:

        route_text = " ".join([
            route["name"],
            route["source"],
            route["destination"],
            route["stops"]
        ]).lower()

        if query in route_text:

            results.append({
                "type": "route",
                "data": route
            })

    for index, stop in enumerate(
        STOP_DATA,
        start=1
    ):

        if query in stop[0].lower():

            results.append({
                "type": "stop",
                "data": {
                    "id": index,
                    "name": stop[0],
                    "latitude": stop[1],
                    "longitude": stop[2]
                }
            })

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results[:30]
    })


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/api/dashboard")
def dashboard():

    return jsonify({
        "success": True,
        "dashboard": {
            "routes": len(ROUTE_DATA),
            "stops": len(STOP_DATA),
            "buses": len(BUS_DATA),
            "traffic_zones": len(TRAFFIC_DATA)
        },
        "system": {
            "status": "operational",
            "routes": [
                route["name"]
                for route in ROUTE_DATA
            ],
            "bus_number_format": "UP53NC0000"
        }
    })


# ============================================================
# ETA
# ============================================================

@app.route("/api/eta")
def eta():

    bus_number = request.args.get("bus")
    route = request.args.get("route")

    selected_bus = None

    for bus in BUS_DATA:

        if (
            bus_number
            and bus["registration"].upper()
            == bus_number.upper()
        ):

            selected_bus = bus
            break

        if (
            route
            and bus["route"].upper()
            == route.upper()
        ):

            selected_bus = bus
            break

    base_eta = (
        selected_bus["eta"]
        if selected_bus
        else random.randint(5, 15)
    )

    traffic_delay = random.choice([
        0,
        0,
        1,
        2,
        3,
        4,
        5
    ])

    if traffic_delay >= 5:
        traffic_status = "High"

    elif traffic_delay >= 2:
        traffic_status = "Moderate"

    else:
        traffic_status = "Low"

    return jsonify({
        "success": True,
        "bus": bus_number,
        "route": route,
        "eta_minutes": (
            base_eta + traffic_delay
        ),
        "traffic_delay_minutes": traffic_delay,
        "traffic_status": traffic_status,
        "updated_at": datetime.now().isoformat()
    })


# ============================================================
# SMART RECOMMENDATIONS — STEP 4
# ============================================================

@app.route("/api/recommend")
def recommend():

    buses = []

    for original in BUS_DATA:

        bus = dict(original)

        state = SIMULATION_STATE[
            bus["id"]
        ]

        bus["latitude"] = state["latitude"]
        bus["longitude"] = state["longitude"]

        bus = simulate_bus(bus)

        buses.append(bus)

    recommendations = []

    for bus in buses:

        recommendation = (
            build_smart_recommendation(bus)
        )

        recommendations.append(
            recommendation
        )

    recommendations.sort(
        key=lambda item:
        item["smart_score"],
        reverse=True
    )

    recommended = recommendations[0]

    return jsonify({
        "success": True,
        "recommended": recommended,
        "recommendations": recommendations,
        "algorithm": {
            "name": "Smart Bus Multi-Factor Recommendation Engine",
            "factors": {
                "eta": "30%",
                "crowd": "25%",
                "safety": "30%",
                "fare": "10%",
                "speed": "8%",
                "traffic": "dynamic penalty",
                "delay": "dynamic penalty"
            }
        },
        "reason": (
            "Recommended using ETA, crowd, safety, "
            "fare, speed, traffic and delay conditions."
        ),
        "updated_at": datetime.now().isoformat()
    })


# ============================================================
# SMART RECOMMENDATION BY ROUTE
# ============================================================

@app.route("/api/recommend/<route_name>")
def recommend_route(route_name):

    route_buses = []

    for original in BUS_DATA:

        if (
            original["route"].upper()
            == route_name.upper()
        ):

            bus = dict(original)

            state = SIMULATION_STATE[
                bus["id"]
            ]

            bus["latitude"] = state["latitude"]
            bus["longitude"] = state["longitude"]

            bus = simulate_bus(bus)

            route_buses.append(
                build_smart_recommendation(bus)
            )

    if not route_buses:

        return jsonify({
            "success": False,
            "message": "No buses found for this route."
        }), 404

    route_buses.sort(
        key=lambda item:
        item["smart_score"],
        reverse=True
    )

    return jsonify({
        "success": True,
        "route": route_name.upper(),
        "recommended": route_buses[0],
        "alternatives": route_buses[1:],
        "count": len(route_buses),
        "updated_at": datetime.now().isoformat()
    })


# ============================================================
# FASTEST
# ============================================================

@app.route("/api/fastest")
def fastest():

    bus = min(
        [
            format_bus(bus)
            for bus in BUS_DATA
        ],
        key=lambda item:
        item["eta"]
    )

    return jsonify({
        "success": True,
        **bus
    })


# ============================================================
# LOWEST CROWD
# ============================================================

@app.route("/api/lowest-crowd")
def lowest_crowd():

    bus = min(
        [
            format_bus(bus)
            for bus in BUS_DATA
        ],
        key=lambda item:
        item["crowd"]
    )

    return jsonify({
        "success": True,
        **bus
    })


# ============================================================
# SAFEST BUS
# ============================================================

@app.route("/api/safest")
def safest():

    bus = max(
        [
            format_bus(bus)
            for bus in BUS_DATA
        ],
        key=lambda item:
        item["safety_score"]
    )

    return jsonify({
        "success": True,
        **bus
    })


# ============================================================
# CHEAPEST BUS
# ============================================================

@app.route("/api/cheapest")
def cheapest():

    bus = min(
        [
            format_bus(bus)
            for bus in BUS_DATA
        ],
        key=lambda item:
        item["fare"]
    )

    return jsonify({
        "success": True,
        **bus
    })


# ============================================================
# EXPENSES
# ============================================================

@app.route("/api/expenses")
def expenses():

    fares = [
        25,
        30,
        35,
        25,
        30,
        40,
        25
    ]

    weekly = sum(fares)
    monthly = weekly * 4

    average = round(
        sum(fares)
        / len(fares)
    )

    return jsonify({
        "success": True,
        "weekly": weekly,
        "monthly": monthly,
        "average": average,
        "trips": len(fares)
    })


# ============================================================
# HISTORY
# ============================================================

@app.route("/api/history")
def history():

    return jsonify([
        {
            "bus": "UP53NC0001",
            "route": "NH24",
            "fare": 25,
            "date": "29/08/2026"
        },
        {
            "bus": "UP53NC0003",
            "route": "NH28",
            "fare": 35,
            "date": "28/08/2026"
        },
        {
            "bus": "UP53NC0007",
            "route": "NH27",
            "fare": 25,
            "date": "27/08/2026"
        }
    ])


# ============================================================
# SMART BUS ASSISTANT
# ============================================================

@app.route("/api/assistant", methods=["POST"])
def assistant():

    data = request.get_json(
        silent=True
    ) or {}

    message = data.get(
        "message",
        ""
    ).strip()

    if not message:

        return jsonify({
            "success": False,
            "message": "Please provide a message."
        }), 400

    text = message.lower()

    if (
        "lowest crowd" in text
        or "least crowd" in text
        or "less crowd" in text
    ):

        bus = min(
            BUS_DATA,
            key=lambda b:
            b["passengers"]
            / b["capacity"]
        )

        crowd = round(
            bus["passengers"]
            / bus["capacity"]
            * 100
        )

        response = (
            f"{bus['registration']} currently has "
            f"the lowest crowd at {crowd}%. "
            f"Its ETA is about {bus['eta']} minutes."
        )

    elif (
        "fastest" in text
        or "quickest" in text
    ):

        bus = min(
            BUS_DATA,
            key=lambda b:
            b["eta"]
        )

        response = (
            f"{bus['registration']} is currently "
            f"the fastest option with an ETA of "
            f"{bus['eta']} minutes."
        )

    elif (
        "safe" in text
        or "safety" in text
        or "safest" in text
    ):

        bus = max(
            BUS_DATA,
            key=lambda b:
            b["safety_score"]
        )

        response = (
            f"{bus['registration']} currently has "
            f"the highest safety score of "
            f"{bus['safety_score']}/100. "
            f"The bus condition is "
            f"{bus['condition']}."
        )

    elif (
        "driver" in text
        or "conductor" in text
    ):

        bus = BUS_DATA[0]

        response = (
            f"{bus['registration']} is operated by "
            f"driver {bus['driver_name']} with "
            f"{bus['driver_experience']} experience. "
            f"Conductor: {bus['conductor_name']} with "
            f"{bus['conductor_experience']} experience."
        )

    elif (
        "best bus" in text
        or "recommend" in text
        or "recommended" in text
    ):

        bus = max(
            BUS_DATA,
            key=lambda b:
            calculate_smart_score(b)
        )

        smart_score = calculate_smart_score(
            bus
        )

        crowd = round(
            bus["passengers"]
            / bus["capacity"]
            * 100
        )

        response = (
            f"I recommend {bus['registration']} "
            f"on {bus['route']}. "
            f"Smart Score: {smart_score}/100. "
            f"ETA: {bus['eta']} minutes, "
            f"crowd: {crowd}%, "
            f"fare: ₹{bus['fare']}, "
            f"safety: {bus['safety_score']}/100."
        )

    elif "nh24" in text:

        response = (
            "NH24 currently has Smart Buses "
            "UP53NC0001 and UP53NC0002."
        )

    elif "nh28" in text:

        response = (
            "NH28 currently has Smart Buses "
            "UP53NC0003 and UP53NC0004."
        )

    elif "nh30" in text:

        response = (
            "NH30 currently has Smart Buses "
            "UP53NC0005 and UP53NC0006."
        )

    elif "nh27" in text:

        response = (
            "NH27 currently has Smart Buses "
            "UP53NC0007 and UP53NC0008."
        )

    elif "traffic" in text:

        response = (
            "Current demo traffic conditions range "
            "from Low to High. Traffic delays can "
            "increase Smart Bus ETA."
        )

    elif (
        "eta" in text
        or "arrival" in text
    ):

        bus = min(
            BUS_DATA,
            key=lambda b:
            b["eta"]
        )

        response = (
            f"The earliest Smart Bus is "
            f"{bus['registration']}, with an ETA "
            f"of approximately {bus['eta']} minutes."
        )

    elif "route" in text:

        response = (
            "The Smart Bus demo currently includes "
            "NH24, NH28, NH30 and NH27."
        )

    elif (
        "expense" in text
        or "spend" in text
        or "cost" in text
    ):

        response = (
            "The demo Smart Bus system tracks "
            "travel fares and calculates weekly "
            "and monthly travel expenses."
        )

    elif (
        "hello" in text
        or "hi" in text
        or "hey" in text
    ):

        response = (
            "Hello! I am your Smart Bus assistant. "
            "You can ask about buses, routes, ETA, "
            "crowd levels, safety or recommendations."
        )

    else:

        response = (
            "I can help with Smart Bus routes, "
            "bus numbers, ETA, crowd levels, "
            "traffic, safety and smart recommendations."
        )

    return jsonify({
        "success": True,
        "user_message": message,
        "response": response
    })


# ============================================================
# API HOME
# ============================================================

@app.route("/api")
def api_home():

    return jsonify({
        "success": True,
        "project": "SIH Smart Bus API",
        "status": "operational",
        "endpoints": [
            "/api/health",
            "/api/system",
            "/api/buses",
            "/api/buses/<bus_number>",
            "/api/buses/<bus_number>/details",
            "/api/live-buses",
            "/api/routes",
            "/api/routes/<route_id>",
            "/api/stops",
            "/api/stops/<stop_id>",
            "/api/traffic",
            "/api/search?q=NH24",
            "/api/dashboard",
            "/api/eta",
            "/api/recommend",
            "/api/recommend/<route_name>",
            "/api/fastest",
            "/api/lowest-crowd",
            "/api/safest",
            "/api/cheapest",
            "/api/expenses",
            "/api/history",
            "/api/assistant"
        ]
    })


# ============================================================
# ERROR HANDLING
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                 SMART BUS BACKEND")
    print("=" * 60)
    print("Routes: NH24 / NH28 / NH30 / NH27")
    print("Bus numbers: UP53NC0001 - UP53NC0008")
    print("Data realism: ENABLED")
    print("Real-time simulation: ENABLED")
    print("Bus movement: ENABLED")
    print("Dynamic ETA: ENABLED")
    print("Dynamic crowd: ENABLED")
    print("Bus safety details: ENABLED")
    print("Driver details: ENABLED")
    print("Conductor details: ENABLED")
    print("Smart recommendation engine: ENABLED")
    print("Multi-factor recommendation: ENABLED")
    print("Traffic-aware recommendation: ENABLED")
    print("Safety-aware recommendation: ENABLED")
    print("Crowd-aware recommendation: ENABLED")
    print("Fare-aware recommendation: ENABLED")
    print("Database:", DATABASE_PATH)
    print("Frontend:", FRONTEND_DIR)
    print("Server: http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )