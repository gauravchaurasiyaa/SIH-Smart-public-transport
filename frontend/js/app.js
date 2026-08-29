const API_URL = "http://127.0.0.1:5000/api";

document.addEventListener("DOMContentLoaded", () => {

    const fromInput = document.getElementById("from");
    const toInput = document.getElementById("to");

    const clearFrom = document.getElementById("clearFrom");
    const clearTo = document.getElementById("clearTo");

    const swapButton = document.getElementById("swapButton");
    const findRoute = document.getElementById("findRoute");

    const results = document.getElementById("results");
    const liveBusGrid = document.getElementById("liveBusGrid");

    const aiMessages = document.getElementById("aiMessages");
    const aiQuestion = document.getElementById("aiQuestion");
    const aiSend = document.getElementById("aiSend");

    const suggestions =
        document.querySelectorAll(".ai-suggestion");

    const travelHistory =
        document.getElementById("travelHistory");


    async function apiRequest(endpoint, options = {}) {

        try {

            const response =
                await fetch(`${API_URL}${endpoint}`, options);

            if (!response.ok) {
                throw new Error("API request failed");
            }

            return await response.json();

        } catch (error) {

            console.error(error);

            return null;
        }
    }


    function getCrowdLevel(crowd) {

        if (crowd < 40) {
            return "Low";
        }

        if (crowd < 65) {
            return "Medium";
        }

        return "High";
    }


    async function displayLiveBuses() {

        const buses =
            await apiRequest("/buses");

        if (!buses) {

            liveBusGrid.innerHTML = `
                <div class="status-card">

                    <div class="status-icon">
                        ⚠️
                    </div>

                    <h2>
                        Backend not connected
                    </h2>

                    <p>
                        Start the Python Flask server
                        to load live bus data.
                    </p>

                </div>
            `;

            return;
        }


        liveBusGrid.innerHTML = "";


        buses.forEach(bus => {

            const crowdLevel =
                getCrowdLevel(bus.crowd);

            const card =
                document.createElement("div");

            card.className =
                "live-bus-card";

            card.innerHTML = `

                <div class="live-bus-top">

                    <span class="bus-number">
                        🚌 ${bus.number}
                    </span>

                    <span class="bus-status">
                        ● ${bus.status}
                    </span>

                </div>

                <div class="live-route">
                    ${bus.route}
                </div>

                <div class="live-location">

                    <span>
                        Current location
                    </span>

                    <strong>
                        ${bus.location}
                    </strong>

                </div>

                <div class="live-next-stop">

                    <span>
                        Next stop
                    </span>

                    <strong>
                        ${bus.nextStop}
                    </strong>

                </div>

                <div class="live-bus-stats">

                    <div class="live-stat">

                        <span>
                            ETA
                        </span>

                        <strong>
                            ${bus.eta} min
                        </strong>

                    </div>

                    <div class="live-stat">

                        <span>
                            FARE
                        </span>

                        <strong>
                            ₹${bus.fare}
                        </strong>

                    </div>

                </div>

                <div class="crowd-bar">

                    <div class="crowd-bar-header">

                        <span>
                            Crowd level
                        </span>

                        <span class="${crowdLevel.toLowerCase()}">
                            ${crowdLevel} · ${bus.crowd}%
                        </span>

                    </div>

                    <div class="crowd-track">

                        <div
                            class="crowd-fill"
                            style="width: ${bus.crowd}%"
                        ></div>

                    </div>

                </div>
            `;

            liveBusGrid.appendChild(card);

        });
    }


    async function searchRoute() {

        const from =
            fromInput.value.trim();

        const to =
            toInput.value.trim();


        if (!from || !to) {

            results.innerHTML = `

                <div class="status-card">

                    <div class="status-icon">
                        ⚠️
                    </div>

                    <h2>
                        Enter both locations
                    </h2>

                    <p>
                        Enter your starting point and
                        destination.
                    </p>

                </div>
            `;

            return;
        }


        results.innerHTML = `

            <div class="status-card">

                <div class="loading-spinner"></div>

                <h2>
                    Finding the best bus...
                </h2>

            </div>
        `;


        const data =
            await apiRequest(
                `/search?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
            );


        if (!data) {

            results.innerHTML = `

                <div class="status-card">

                    <div class="status-icon">
                        ⚠️
                    </div>

                    <h2>
                        Unable to connect
                    </h2>

                    <p>
                        Please make sure the Flask
                        backend is running.
                    </p>

                </div>
            `;

            return;
        }


        const recommended =
            data.recommended;


        results.innerHTML = `

            <div class="route-result">

                <span class="recommended-badge">
                    AI RECOMMENDATION
                </span>

                <h2>
                    ${data.from} → ${data.to}
                </h2>

                <h3>
                    Best available option
                </h3>

                <div class="route-meta">

                    <span>
                        🚌 ${recommended.number}
                    </span>

                    <span>
                        ⏱ ${recommended.eta} min
                    </span>

                    <span>
                        👥 ${getCrowdLevel(
                            recommended.crowd
                        )} crowd
                    </span>

                    <span>
                        ₹${recommended.fare}
                    </span>

                </div>

            </div>


            <div class="smart-recommendation">

                <div class="recommendation-title">
                    WHY THIS BUS?
                </div>

                <div class="recommendation-bus">
                    🚌 ${recommended.number}
                </div>

                <div class="recommendation-details">
                    ${recommended.route}
                    · ETA ${recommended.eta} minutes
                    · ₹${recommended.fare}
                </div>

                <div class="recommendation-reason">
                    Recommended using ETA and crowd
                    level together.
                </div>

            </div>


            <div class="bus-grid">

                ${data.buses.map(bus => `

                    <div class="bus-result">

                        <h3>
                            🚌 ${bus.number}
                        </h3>

                        <div class="bus-status-row">

                            <span>
                                ${bus.status}
                            </span>

                            <span>
                                ETA ${bus.eta} min
                            </span>

                        </div>

                        <div class="occupancy-box">

                            <div class="occupancy-header">

                                <span>
                                    Crowd
                                </span>

                                <strong>
                                    ${getCrowdLevel(bus.crowd)}
                                </strong>

                            </div>

                            <div class="occupancy-track">

                                <div
                                    class="occupancy-fill"
                                    style="width:${bus.crowd}%"
                                ></div>

                            </div>

                        </div>

                        <div class="bus-detail">

                            <span class="bus-detail-label">
                                Route
                            </span>

                            <span class="bus-detail-value">
                                ${bus.route}
                            </span>

                        </div>

                        <div class="bus-detail">

                            <span class="bus-detail-label">
                                Next stop
                            </span>

                            <span class="bus-detail-value">
                                ${bus.nextStop}
                            </span>

                        </div>

                        <div class="bus-detail">

                            <span class="bus-detail-label">
                                Fare
                            </span>

                            <span class="bus-detail-value">
                                ₹${bus.fare}
                            </span>

                        </div>

                    </div>

                `).join("")}

            </div>
        `;


        results.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }


    async function displayHistory() {

        const history =
            await apiRequest("/history");


        if (!history) {

            travelHistory.innerHTML = `

                <div class="status-card">

                    <div class="status-icon">
                        ⚠️
                    </div>

                    <h2>
                        Backend not connected
                    </h2>

                </div>
            `;

            return;
        }


        if (!history.length) {

            travelHistory.innerHTML = `

                <div class="status-card">

                    <div class="status-icon">
                        🧾
                    </div>

                    <h2>
                        No travel history
                    </h2>

                </div>
            `;

            return;
        }


        travelHistory.innerHTML =
            history.map(item => `

                <div class="history-card">

                    <div class="history-bus">

                        <div class="history-bus-icon">
                            🚌
                        </div>

                        <div>

                            <strong>
                                ${item.bus}
                            </strong>

                            <span>
                                ${item.date}
                            </span>

                        </div>

                    </div>

                    <div class="history-route">

                        <span>
                            ${item.route}
                        </span>

                    </div>

                    <div class="history-fare">

                        <strong>
                            ₹${item.fare}
                        </strong>

                        <span>
                            Bus fare
                        </span>

                    </div>

                </div>

            `).join("");
    }


    async function updateExpenses() {

        const data =
            await apiRequest("/expenses");


        if (!data) {
            return;
        }


        const weeklyExpense =
            document.getElementById(
                "weeklyExpense"
            );

        const monthlyExpense =
            document.getElementById(
                "monthlyExpense"
            );

        const averageFare =
            document.getElementById(
                "averageFare"
            );

        const weeklyTrips =
            document.getElementById(
                "weeklyTrips"
            );

        const monthlyTrips =
            document.getElementById(
                "monthlyTrips"
            );


        weeklyExpense.textContent =
            `₹${data.weekly}`;

        monthlyExpense.textContent =
            `₹${data.monthly}`;

        averageFare.textContent =
            `₹${data.average}`;

        weeklyTrips.textContent =
            `${data.trips} trips`;

        monthlyTrips.textContent =
            `${data.trips} trips`;
    }


    async function getAIResponse(question) {

        const text =
            question.toLowerCase();


        if (
            text.includes("lowest crowd") ||
            text.includes("less crowd") ||
            text.includes("least crowd")
        ) {

            const bus =
                await apiRequest(
                    "/lowest-crowd"
                );

            if (!bus) {
                return "Backend is not connected.";
            }

            return `
                ${bus.number} currently has the
                lowest crowd level at ${bus.crowd}%.
                Its estimated arrival is ${bus.eta}
                minutes.
            `;
        }


        if (
            text.includes("fastest") ||
            text.includes("quick")
        ) {

            const bus =
                await apiRequest(
                    "/fastest"
                );

            if (!bus) {
                return "Backend is not connected.";
            }

            return `
                ${bus.number} is currently the fastest
                option with an estimated arrival of
                ${bus.eta} minutes.
            `;
        }


        if (
            text.includes("best bus") ||
            text.includes("recommend")
        ) {

            const data =
                await apiRequest(
                    "/recommend"
                );

            if (!data) {
                return "Backend is not connected.";
            }

            const bus =
                data.recommended;

            return `
                I recommend ${bus.number}.
                It arrives in about ${bus.eta} minutes,
                has ${getCrowdLevel(
                    bus.crowd
                ).toLowerCase()}
                crowd, and costs ₹${bus.fare}.
            `;
        }


        if (
            text.includes("expense") ||
            text.includes("spend") ||
            text.includes("cost")
        ) {

            const data =
                await apiRequest(
                    "/expenses"
                );

            if (!data) {
                return "Backend is not connected.";
            }

            return `
                Your recorded travel expense is
                ₹${data.monthly} across
                ${data.trips} trips.
            `;
        }


        if (
            text.includes("eta") ||
            text.includes("arrival")
        ) {

            const bus =
                await apiRequest(
                    "/fastest"
                );

            if (!bus) {
                return "Backend is not connected.";
            }

            return `
                The earliest available bus is
                ${bus.number}, arriving in about
                ${bus.eta} minutes.
            `;
        }


        if (
            text.includes("crowd") ||
            text.includes("busy")
        ) {

            const bus =
                await apiRequest(
                    "/lowest-crowd"
                );

            if (!bus) {
                return "Backend is not connected.";
            }

            return `
                ${bus.number} currently has the
                lowest crowd level at ${bus.crowd}%.
            `;
        }


        return `
            I can help with bus recommendations,
            ETA, crowd levels, routes and travel
            expenses.
        `;
    }


    function addAIMessage(
        text,
        user = false
    ) {

        const message =
            document.createElement("div");

        message.className =
            user
                ? "ai-message ai-user"
                : "ai-message ai-bot";


        if (user) {

            message.innerHTML = `

                <div class="ai-message-content">

                    <strong>
                        You
                    </strong>

                    <p>
                        ${text}
                    </p>

                </div>

                <div class="ai-avatar">
                    👤
                </div>

            `;

        } else {

            message.innerHTML = `

                <div class="ai-avatar">
                    🤖
                </div>

                <div class="ai-message-content">

                    <strong>
                        Smart Bus AI
                    </strong>

                    <p>
                        ${text}
                    </p>

                </div>

            `;
        }


        aiMessages.appendChild(message);

        aiMessages.scrollTop =
            aiMessages.scrollHeight;
    }


    async function sendAIMessage() {

        const question =
            aiQuestion.value.trim();


        if (!question) {
            return;
        }


        addAIMessage(
            question,
            true
        );

        aiQuestion.value = "";


        const response =
            await getAIResponse(question);

        addAIMessage(response);
    }


    findRoute.addEventListener(
        "click",
        searchRoute
    );


    swapButton.addEventListener(
        "click",
        () => {

            const temp =
                fromInput.value;

            fromInput.value =
                toInput.value;

            toInput.value =
                temp;
        }
    );


    clearFrom.addEventListener(
        "click",
        () => {

            fromInput.value = "";

            fromInput.focus();
        }
    );


    clearTo.addEventListener(
        "click",
        () => {

            toInput.value = "";

            toInput.focus();
        }
    );


    fromInput.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {
                searchRoute();
            }
        }
    );


    toInput.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {
                searchRoute();
            }
        }
    );


    aiSend.addEventListener(
        "click",
        sendAIMessage
    );


    aiQuestion.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {
                sendAIMessage();
            }
        }
    );


    suggestions.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                aiQuestion.value =
                    button.dataset.question;

                sendAIMessage();
            }
        );

    });


    displayLiveBuses();

    displayHistory();

    updateExpenses();

});