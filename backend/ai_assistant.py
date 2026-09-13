def get_transport_response(
    question,
    buses,
    routes,
    stops
):

    question = (
        question
        .lower()
        .strip()
    )

    if not question:

        return (
            "Please ask me something about "
            "buses, routes, ETA, traffic or crowding."
        )


    if (
        "hello" in question
        or "hi" in question
        or "hey" in question
    ):

        return (
            "Hello! I am the Smart Bus assistant. "
            "You can ask me about bus locations, "
            "routes, ETA, delays, traffic or crowd levels."
        )


    if (
        "delay" in question
        or "late" in question
    ):

        delayed = [
            bus
            for bus in buses
            if bus["status"] == "delayed"
        ]

        if not delayed:

            return (
                "Currently no Smart Bus is marked "
                "as delayed."
            )

        details = []

        for bus in delayed:

            details.append(
                f"{bus['registration']} on "
                f"route {bus['route_id']}"
            )

        return (
            "Delayed buses: "
            + ", ".join(details)
            + "."
        )


    if (
        "crowd" in question
        or "crowded" in question
        or "occupancy" in question
    ):

        crowded = []

        for bus in buses:

            percentage = (
                bus["passengers"]
                /
                bus["capacity"]
            ) * 100

            if percentage >= 70:

                crowded.append(
                    f"{bus['registration']} "
                    f"({round(percentage)}% occupied)"
                )

        if not crowded:

            return (
                "No Smart Bus currently has "
                "high occupancy."
            )

        return (
            "High occupancy buses: "
            + ", ".join(crowded)
            + "."
        )


    if "route" in question:

        route_names = [
            route["id"]
            for route in routes
        ]

        return (
            "Available routes are "
            + ", ".join(route_names)
            + "."
        )


    if "bus" in question:

        return (
            f"There are currently "
            f"{len(buses)} buses in the demo system."
        )


    if "stop" in question:

        return (
            f"There are currently "
            f"{len(stops)} registered bus stops."
        )


    if "eta" in question:

        return (
            "ETA is calculated using the current "
            "bus location, speed and traffic conditions."
        )


    return (
        "I can help with Smart Bus locations, "
        "routes such as NH24 and NH28, ETA, "
        "traffic, delays and crowd levels."
    )