ROUTES = [
    {
        "id": "NH24",
        "name": "NH24",
        "source": "Ghaziabad",
        "destination": "Delhi",
        "stops": [
            "Ghaziabad",
            "Vijay Nagar",
            "Anand Vihar",
            "Kaushambi",
            "Delhi"
        ]
    },
    {
        "id": "NH28",
        "name": "NH28",
        "source": "Lucknow",
        "destination": "Gorakhpur",
        "stops": [
            "Lucknow",
            "Ayodhya",
            "Basti",
            "Gorakhpur"
        ]
    },
    {
        "id": "NH30",
        "name": "NH30",
        "source": "Lucknow",
        "destination": "Kanpur",
        "stops": [
            "Lucknow",
            "Unnao",
            "Kanpur"
        ]
    },
    {
        "id": "NH27",
        "name": "NH27",
        "source": "Gorakhpur",
        "destination": "Ayodhya",
        "stops": [
            "Gorakhpur",
            "Basti",
            "Ayodhya"
        ]
    }
]


STOPS = [
    {
        "id": "ST01",
        "name": "Ghaziabad",
        "latitude": 28.6692,
        "longitude": 77.4538
    },
    {
        "id": "ST02",
        "name": "Vijay Nagar",
        "latitude": 28.6692,
        "longitude": 77.4350
    },
    {
        "id": "ST03",
        "name": "Anand Vihar",
        "latitude": 28.6469,
        "longitude": 77.3160
    },
    {
        "id": "ST04",
        "name": "Kaushambi",
        "latitude": 28.6455,
        "longitude": 77.3240
    },
    {
        "id": "ST05",
        "name": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090
    },
    {
        "id": "ST06",
        "name": "Lucknow",
        "latitude": 26.8467,
        "longitude": 80.9462
    },
    {
        "id": "ST07",
        "name": "Ayodhya",
        "latitude": 26.7997,
        "longitude": 82.2043
    },
    {
        "id": "ST08",
        "name": "Basti",
        "latitude": 26.8014,
        "longitude": 82.7274
    },
    {
        "id": "ST09",
        "name": "Gorakhpur",
        "latitude": 26.7606,
        "longitude": 83.3732
    },
    {
        "id": "ST10",
        "name": "Unnao",
        "latitude": 26.5471,
        "longitude": 80.4878
    },
    {
        "id": "ST11",
        "name": "Kanpur",
        "latitude": 26.4499,
        "longitude": 80.3319
    }
]


BUSES = [
    {
        "id": "BUS001",
        "registration": "UP53NC1024",
        "route_id": "NH24",
        "capacity": 50,
        "passengers": 32,
        "latitude": 28.6600,
        "longitude": 77.4200,
        "speed": 42,
        "status": "on-time"
    },
    {
        "id": "BUS002",
        "registration": "UP53NC2048",
        "route_id": "NH24",
        "capacity": 50,
        "passengers": 44,
        "latitude": 28.6500,
        "longitude": 77.3500,
        "speed": 31,
        "status": "delayed"
    },
    {
        "id": "BUS003",
        "registration": "UP53NC3096",
        "route_id": "NH28",
        "capacity": 52,
        "passengers": 24,
        "latitude": 26.9000,
        "longitude": 81.2000,
        "speed": 55,
        "status": "on-time"
    },
    {
        "id": "BUS004",
        "registration": "UP53NC4012",
        "route_id": "NH28",
        "capacity": 52,
        "passengers": 47,
        "latitude": 26.8200,
        "longitude": 82.0000,
        "speed": 38,
        "status": "crowded"
    },
    {
        "id": "BUS005",
        "registration": "UP53NC5099",
        "route_id": "NH30",
        "capacity": 45,
        "passengers": 19,
        "latitude": 26.7000,
        "longitude": 80.7500,
        "speed": 48,
        "status": "on-time"
    },
    {
        "id": "BUS006",
        "registration": "UP53NC6018",
        "route_id": "NH27",
        "capacity": 50,
        "passengers": 41,
        "latitude": 26.7900,
        "longitude": 82.4500,
        "speed": 35,
        "status": "delayed"
    }
]


TRAFFIC = [
    {
        "id": 1,
        "location": "Ghaziabad",
        "level": "high",
        "delay_minutes": 8
    },
    {
        "id": 2,
        "location": "Anand Vihar",
        "level": "medium",
        "delay_minutes": 4
    },
    {
        "id": 3,
        "location": "Ayodhya",
        "level": "low",
        "delay_minutes": 1
    },
    {
        "id": 4,
        "location": "Basti",
        "level": "medium",
        "delay_minutes": 5
    },
    {
        "id": 5,
        "location": "Lucknow",
        "level": "high",
        "delay_minutes": 9
    },
    {
        "id": 6,
        "location": "Kanpur",
        "level": "medium",
        "delay_minutes": 4
    }
]