/* ============================================================
   SMART BUS FRONTEND
============================================================ */

const API_BASE = "/api";

let busMap = null;
let busMarkers = {};
let mapInitialized = false;
let incidentMarkers = {};


/* ============================================================
   DOM READY
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    initializeMap();
    loadLiveBuses();
    loadExpenses();
    loadHistory();
    setupRouteSearch();
    setupAI();
    setupClearButtons();
    setupSwapButton();
});


/* ============================================================
   API HELPER
============================================================ */

async function apiFetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, options);

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(
            data?.error ||
            data?.message ||
            `Request failed with status ${response.status}`
        );
    }

    return data;
}


/* ============================================================
   MAP
============================================================ */

function initializeMap() {
    const mapElement = document.getElementById("busMap");

    if (!mapElement) {
        return;
    }

    if (typeof L === "undefined") {
        console.error("Leaflet is not loaded.");
        return;
    }

    try {
        busMap = L.map("busMap", {
            zoomControl: true,
            scrollWheelZoom: true
        }).setView([27.25, 81.5], 6);

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
            }
        ).addTo(busMap);

        mapInitialized = true;

    } catch (error) {
        console.error("Map initialization failed:", error);
    }
}


/* ============================================================
   BUS ICON
============================================================ */

function createBusIcon() {
    return L.divIcon({
        className: "custom-bus-icon-wrapper",

        html: `
            <div class="custom-bus-marker">
                🚌
            </div>
        `,

        iconSize: [38, 38],
        iconAnchor: [19, 19],
        popupAnchor: [0, -20]
    });
}


/* ============================================================
   LOAD LIVE BUSES
============================================================ */

async function loadLiveBuses() {
    try {
        const data = await apiFetch("/live-buses");

        const buses = Array.isArray(data?.buses)
            ? data.buses
            : [];

        renderLiveBusCards(buses);
        updateBusMap(buses);
        renderMapBusList(buses);
        updateAuthorityDashboard(buses);

    } catch (error) {
        console.error("Live bus loading failed:", error);

        const grid = document.getElementById("liveBusGrid");

        if (grid) {
            grid.innerHTML = `
                <div class="status-card">
                    <div class="status-icon">⚠️</div>

                    <h2>
                        Unable to load buses
                    </h2>

                    <p>
                        Make sure the Flask backend is running.
                    </p>
                </div>
            `;
        }
    }
}


/* ============================================================
   UPDATE BUS MAP
============================================================ */

function updateBusMap(buses) {
    if (!mapInitialized || !busMap) {
        return;
    }

    const bounds = [];

    buses.forEach(bus => {
        const latitude = Number(bus?.latitude);
        const longitude = Number(bus?.longitude);

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude)
        ) {
            return;
        }

        bounds.push([latitude, longitude]);

        const busId = bus.id ?? bus.number;

        const popup = `
            <div class="smart-bus-popup">

                <div class="map-popup-title">
                    🚌 ${escapeHtml(bus.number)}
                </div>

                <div class="map-popup-route">
                    ${escapeHtml(bus.route)}
                </div>

                <div class="map-popup-row">
                    <span>Location</span>
                    <strong>
                        ${escapeHtml(bus.location)}
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Next Stop</span>
                    <strong>
                        ${escapeHtml(bus.next_stop)}
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>ETA</span>
                    <strong>
                        ${escapeHtml(bus.eta)} min
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Crowd</span>
                    <strong>
                        ${escapeHtml(bus.crowd)}%
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Speed</span>
                    <strong>
                        ${escapeHtml(bus.speed)} km/h
                    </strong>
                </div>

                <button
                    type="button"
                    class="view-bus-details map-details-button"
                    data-bus-number="${escapeHtml(bus.number)}"
                >
                    View Full Details
                </button>

            </div>
        `;

        if (busMarkers[busId]) {

            /*
             * STEP 1:
             * Smoothly move the existing bus marker
             * to the newest simulated GPS position.
             */
            animateBusMarker(
                busMarkers[busId],
                latitude,
                longitude,
                1800
            );

            busMarkers[busId].setPopupContent(popup);

        } else {

            const marker = L.marker(
                [latitude, longitude],
                {
                    icon: createBusIcon()
                }
            )
                .addTo(busMap)
                .bindPopup(popup);

            busMarkers[busId] = marker;
        }
    });

    if (
        bounds.length > 0 &&
        !busMap._smartBusFitted
    ) {
        try {
            busMap.fitBounds(
                bounds,
                {
                    padding: [45, 45]
                }
            );

            busMap._smartBusFitted = true;

        } catch (error) {
            console.error(
                "Map bounds error:",
                error
            );
        }
    }
}


/* ============================================================
   SMOOTH BUS MARKER MOVEMENT
============================================================ */

function animateBusMarker(
    marker,
    targetLatitude,
    targetLongitude,
    duration = 1800
) {
    if (!marker) {
        return;
    }

    const startPosition =
        marker.getLatLng();

    const startLatitude =
        startPosition.lat;

    const startLongitude =
        startPosition.lng;

    const startTime =
        performance.now();

    if (marker._animationFrame) {
        cancelAnimationFrame(
            marker._animationFrame
        );
    }

    function animate(currentTime) {

        const elapsed =
            currentTime - startTime;

        const progress =
            Math.min(
                elapsed / duration,
                1
            );

        /*
         * Ease-in-out movement so the bus
         * does not visually jump.
         */
        const eased =
            progress < 0.5
                ? 2 * progress * progress
                : 1 -
                    Math.pow(
                        -2 * progress + 2,
                        2
                    ) / 2;

        const currentLatitude =
            startLatitude +
            (
                targetLatitude -
                startLatitude
            ) * eased;

        const currentLongitude =
            startLongitude +
            (
                targetLongitude -
                startLongitude
            ) * eased;

        marker.setLatLng([
            currentLatitude,
            currentLongitude
        ]);

        if (progress < 1) {

            marker._animationFrame =
                requestAnimationFrame(
                    animate
                );

        } else {

            marker.setLatLng([
                targetLatitude,
                targetLongitude
            ]);

            marker._animationFrame = null;
        }
    }

    marker._animationFrame =
        requestAnimationFrame(
            animate
        );
}


/* ============================================================
   MAP BUS LIST
============================================================ */

function renderMapBusList(buses) {
    const container =
        document.getElementById("mapBusList");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!buses.length) {
        container.innerHTML = `
            <div class="status-card">
                <p>No live buses available.</p>
            </div>
        `;

        return;
    }

    buses.forEach(bus => {
        const item =
            document.createElement("div");

        item.className =
            "map-bus-item";

        item.innerHTML = `
            <div class="map-bus-item-top">

                <span class="map-bus-number">
                    🚌 ${escapeHtml(bus.number)}
                </span>

                <span class="map-bus-status">
                    ${escapeHtml(bus.status)}
                </span>

            </div>

            <div class="map-bus-route">
                ${escapeHtml(bus.route)}
            </div>

            <div class="map-bus-eta">
                📍 ${escapeHtml(bus.location)}
                • ETA ${escapeHtml(bus.eta)} min
            </div>
        `;

        item.addEventListener(
            "click",
            () => {
                focusBusOnMap(bus);
            }
        );

        container.appendChild(item);
    });
}


/* ============================================================
   FOCUS BUS ON MAP
============================================================ */

function focusBusOnMap(bus) {
    if (!busMap) {
        return;
    }

    const busId =
        bus.id ?? bus.number;

    const marker =
        busMarkers[busId];

    if (!marker) {
        return;
    }

    const latitude =
        Number(bus.latitude);

    const longitude =
        Number(bus.longitude);

    if (
        !Number.isFinite(latitude) ||
        !Number.isFinite(longitude)
    ) {
        return;
    }

    busMap.setView(
        [latitude, longitude],
        13,
        {
            animate: true
        }
    );

    marker.openPopup();
}


/* ============================================================
   LIVE BUS CARDS
============================================================ */

function renderLiveBusCards(buses) {
    const grid =
        document.getElementById(
            "liveBusGrid"
        );

    if (!grid) {
        return;
    }

    grid.innerHTML = "";

    if (!buses.length) {
        grid.innerHTML = `
            <div class="status-card">
                <div class="status-icon">🚌</div>

                <h2>
                    No live buses
                </h2>

                <p>
                    No bus information is currently available.
                </p>
            </div>
        `;

        return;
    }

    buses.forEach(bus => {

        const crowdClass =
            getCrowdClass(bus.crowd);

        const card =
            document.createElement("div");

        card.className =
            "live-bus-card";

        card.innerHTML = `
            <div class="live-bus-top">

                <span class="bus-number">
                    ${escapeHtml(bus.number)}
                </span>

                <span class="bus-status">
                    ${escapeHtml(bus.status)}
                </span>

            </div>

            <div class="live-route">
                ${escapeHtml(bus.route)}
            </div>

            <div class="live-location">

                <span>
                    CURRENT
                </span>

                <strong>
                    ${escapeHtml(bus.location)}
                </strong>

            </div>

            <div class="live-next-stop">

                <span>
                    NEXT STOP
                </span>

                <strong>
                    ${escapeHtml(bus.next_stop)}
                </strong>

            </div>

            <div class="live-bus-stats">

                <div class="live-stat">

                    <span>
                        ETA
                    </span>

                    <strong>
                        ${escapeHtml(bus.eta)} min
                    </strong>

                </div>

                <div class="live-stat">

                    <span>
                        SPEED
                    </span>

                    <strong>
                        ${escapeHtml(bus.speed)} km/h
                    </strong>

                </div>

            </div>

            <div class="crowd-bar">

                <div class="crowd-bar-header">

                    <span>
                        CROWD
                    </span>

                    <strong class="${crowdClass}">
                        ${escapeHtml(bus.crowd)}%
                    </strong>

                </div>

                <div class="crowd-track">

                    <div
                        class="crowd-fill"
                        style="width:${safePercentage(bus.crowd)}%"
                    ></div>

                </div>

            </div>

            <button
                type="button"
                class="view-bus-details"
                data-bus-number="${escapeHtml(bus.number)}"
            >
                View Full Details →
            </button>
        `;

        grid.appendChild(card);
    });
}


/* ============================================================
   CROWD CLASS
============================================================ */

function getCrowdClass(crowd) {
    const value =
        Number(crowd);

    if (!Number.isFinite(value)) {
        return "medium";
    }

    if (value < 40) {
        return "low";
    }

    if (value < 75) {
        return "medium";
    }

    return "high";
}


/* ============================================================
   SAFE PERCENTAGE
============================================================ */

function safePercentage(value) {
    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return 0;
    }

    return Math.min(
        100,
        Math.max(
            0,
            number
        )
    );
}


/* ============================================================
   REAL-TIME AUTO REFRESH
============================================================ */

/*
 * STEP 1:
 * Previously the live bus data was refreshed every 15 seconds.
 *
 * Now it refreshes every 2 seconds.
 *
 * The backend simulation changes GPS coordinates
 * and the frontend smoothly moves the existing marker.
 */

setInterval(() => {
    loadLiveBuses();
}, 2000);


/* ============================================================
   ROUTE SEARCH SETUP
============================================================ */

function setupRouteSearch() {
    const findButton =
        document.getElementById(
            "findRoute"
        );

    const fromInput =
        document.getElementById(
            "from"
        );

    const toInput =
        document.getElementById(
            "to"
        );

    if (findButton) {
        findButton.addEventListener(
            "click",
            findBestRoute
        );
    }

    if (fromInput) {
        fromInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {
                    findBestRoute();
                }

            }
        );
    }

    if (toInput) {
        toInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {
                    findBestRoute();
                }

            }
        );
    }
}


/* ============================================================
   FIND BEST ROUTE
============================================================ */

async function findBestRoute() {
    const from =
        document.getElementById(
            "from"
        )?.value.trim();

    const to =
        document.getElementById(
            "to"
        )?.value.trim();

    const results =
        document.getElementById(
            "results"
        );

    if (!results) {
        return;
    }

    if (!from || !to) {

        results.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    📍
                </div>

                <h2>
                    Enter both locations
                </h2>

                <p>
                    Please enter your starting point
                    and destination.
                </p>

            </div>
        `;

        return;
    }

    if (
        from.toLowerCase() ===
        to.toLowerCase()
    ) {

        results.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    📍
                </div>

                <h2>
                    Locations are the same
                </h2>

                <p>
                    Please choose a different destination.
                </p>

            </div>
        `;

        return;
    }

    results.innerHTML = `
        <div class="status-card">

            <div class="loading-spinner"></div>

            <h2>
                Finding your best bus...
            </h2>

            <p>
                Comparing ETA and crowd levels.
            </p>

        </div>
    `;

    try {

        const search =
            await apiFetch(
                `/search?q=${encodeURIComponent(to)}`
            );

        const recommendation =
            await apiFetch(
                "/recommend"
            );

        const busesResponse =
            await apiFetch(
                "/buses"
            );

        renderRouteResults(
            from,
            to,
            search,
            recommendation,
            busesResponse
        );

    } catch (error) {

        console.error(
            "Route search failed:",
            error
        );

        results.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    ⚠️
                </div>

                <h2>
                    Search unavailable
                </h2>

                <p>
                    ${escapeHtml(
                        error.message ||
                        "Please check whether the Flask backend is running."
                    )}
                </p>

            </div>
        `;
    }
}


/* ============================================================
   ROUTE RESULTS
============================================================ */

function renderRouteResults(
    from,
    to,
    search,
    recommendation,
    busesResponse
) {
    const results =
        document.getElementById(
            "results"
        );

    if (!results) {
        return;
    }

    const bus =
        recommendation?.recommended;

    if (!bus) {

        results.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    🚌
                </div>

                <h2>
                    No bus recommendation found
                </h2>

                <p>
                    Try another route.
                </p>

            </div>
        `;

        return;
    }

    const allBuses =
        Array.isArray(
            busesResponse?.buses
        )
            ? busesResponse.buses
            : [];

    const destination =
        String(to).toLowerCase();

    const matchingBuses =
        allBuses.filter(item => {

            const route =
                String(
                    item?.route || ""
                ).toLowerCase();

            const location =
                String(
                    item?.location || ""
                ).toLowerCase();

            const nextStop =
                String(
                    item?.next_stop || ""
                ).toLowerCase();

            return (
                route.includes(destination) ||
                location.includes(destination) ||
                nextStop.includes(destination)
            );
        });

    results.innerHTML = `
        <div class="route-result">

            <span class="recommended-badge">
                SMART ROUTE FOUND
            </span>

            <h2>
                ${escapeHtml(from)}
                →
                ${escapeHtml(to)}
            </h2>

            <h3>
                Recommended Smart Bus
            </h3>

            <div class="route-meta">

                <span>
                    🚌 ${escapeHtml(bus.number)}
                </span>

                <span>
                    ⚡ ${escapeHtml(bus.eta)} min ETA
                </span>

                <span>
                    👥 ${escapeHtml(bus.crowd)}% crowd
                </span>

                <span>
                    💰 ₹${escapeHtml(bus.fare)}
                </span>

            </div>

            <button
                type="button"
                class="view-bus-details"
                data-bus-number="${escapeHtml(bus.number)}"
            >
                View Full Details →
            </button>

        </div>

        <div class="smart-recommendation">

            <div class="recommendation-title">
                AI RECOMMENDATION
            </div>

            <div class="recommendation-bus">
                ${escapeHtml(bus.number)}
            </div>

            <div class="recommendation-details">
                ${escapeHtml(bus.route)}
                •
                ${escapeHtml(bus.eta)} min
                •
                ₹${escapeHtml(bus.fare)}
                •
                ${escapeHtml(bus.crowd)}% crowd
            </div>

            <div class="recommendation-reason">
                Best balance of arrival time
                and crowd level.
            </div>

        </div>

        ${
            matchingBuses.length > 0
                ? `
                    <div class="bus-grid">

                        ${matchingBuses
                            .slice(0, 3)
                            .map(createBusResult)
                            .join("")}

                    </div>
                `
                : ""
        }
    `;
}


/* ============================================================
   BUS RESULT
============================================================ */

function createBusResult(bus) {

    const crowdClass =
        getCrowdClass(bus.crowd);

    return `
        <div class="bus-result">

            <h3>
                🚌 ${escapeHtml(bus.number)}
            </h3>

            <div class="bus-status-row">

                <span>
                    ${escapeHtml(bus.route)}
                </span>

                <span>
                    ${escapeHtml(bus.eta)} min
                </span>

            </div>

            <div class="occupancy-box">

                <div class="occupancy-header">

                    <span>
                        Crowd
                    </span>

                    <strong class="${crowdClass}">
                        ${escapeHtml(bus.crowd)}%
                    </strong>

                </div>

                <div class="occupancy-track">

                    <div
                        class="occupancy-fill"
                        style="width:${safePercentage(bus.crowd)}%"
                    ></div>

                </div>

            </div>

            <div class="bus-detail">

                <span class="bus-detail-label">
                    Current
                </span>

                <span class="bus-detail-value">
                    ${escapeHtml(bus.location)}
                </span>

            </div>

            <div class="bus-detail">

                <span class="bus-detail-label">
                    Next stop
                </span>

                <span class="bus-detail-value">
                    ${escapeHtml(bus.next_stop)}
                </span>

            </div>

            <div class="bus-detail">

                <span class="bus-detail-label">
                    Fare
                </span>

                <span class="bus-detail-value">
                    ₹${escapeHtml(bus.fare)}
                </span>

            </div>

            <button
                type="button"
                class="view-bus-details"
                data-bus-number="${escapeHtml(bus.number)}"
            >
                View Full Details →
            </button>

        </div>
    `;
}


/* ============================================================
   BUS DETAILS BUTTON
============================================================ */

document.addEventListener(
    "click",
    event => {

        const button =
            event.target.closest(
                ".view-bus-details"
            );

        if (!button) {
            return;
        }

        const busNumber =
            button.getAttribute(
                "data-bus-number"
            );

        if (busNumber) {
            showBusDetails(
                busNumber
            );
        }
    }
);


/* ============================================================
   SHOW BUS DETAILS
============================================================ */

async function showBusDetails(busNumber) {

    let button = null;

    try {

        const buttons =
            document.querySelectorAll(
                ".view-bus-details"
            );

        for (const item of buttons) {

            if (
                item.getAttribute(
                    "data-bus-number"
                ) === busNumber
            ) {

                button = item;
                break;
            }
        }

        if (button) {

            button.disabled = true;

            button.dataset.originalText =
                button.innerHTML;

            button.innerHTML =
                "Loading Details...";
        }

        const data =
            await apiFetch(
                `/buses/${encodeURIComponent(busNumber)}/details`
            );

        if (
            !data ||
            !data.success ||
            !data.bus
        ) {
            throw new Error(
                data?.error ||
                "Bus details were not returned by the server."
            );
        }

        const bus =
            data.bus;

        const oldModal =
            document.getElementById(
                "busDetailsModal"
            );

        if (oldModal) {
            oldModal.remove();
        }

        const modal =
            document.createElement(
                "div"
            );

        modal.id =
            "busDetailsModal";

        modal.className =
            "bus-details-modal";

        modal.innerHTML = `
            <div class="bus-details-overlay">

                <div
                    class="bus-details-content"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="busDetailsTitle"
                >

                    <div class="bus-details-header">

                        <div>

                            <span class="details-label">
                                SMART BUS
                            </span>

                            <h2 id="busDetailsTitle">
                                🚌 ${escapeHtml(
                                    bus.number ||
                                    busNumber
                                )}
                            </h2>

                            <p>
                                ${escapeHtml(
                                    bus.route ||
                                    "Route information unavailable"
                                )}
                            </p>

                        </div>

                        <button
                            type="button"
                            class="bus-details-close"
                            id="closeBusDetails"
                            aria-label="Close"
                        >
                            ×
                        </button>

                    </div>

                    <div class="details-section">

                        <h3>
                            📍 Live Information
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Registration",
                                bus.registration
                            )}

                            ${detailItem(
                                "Route",
                                bus.route
                            )}

                            ${detailItem(
                                "Current Location",
                                bus.location
                            )}

                            ${detailItem(
                                "Next Stop",
                                bus.next_stop
                            )}

                            ${detailItem(
                                "ETA",
                                formatValue(
                                    bus.eta,
                                    " min"
                                )
                            )}

                            ${detailItem(
                                "Speed",
                                formatValue(
                                    bus.speed,
                                    " km/h"
                                )
                            )}

                            ${detailItem(
                                "Status",
                                bus.status
                            )}

                            ${detailItem(
                                "Fare",
                                formatValue(
                                    bus.fare,
                                    "",
                                    "₹"
                                )
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            👥 Passenger Information
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Bus Capacity",
                                formatValue(
                                    bus.capacity,
                                    " passengers"
                                )
                            )}

                            ${detailItem(
                                "Current Passengers",
                                bus.passengers
                            )}

                            ${detailItem(
                                "Crowd Level",
                                formatValue(
                                    bus.crowd,
                                    "%"
                                ),
                                getCrowdClass(
                                    bus.crowd
                                )
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            🛡️ Bus Safety & Condition
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Safety Score",
                                formatValue(
                                    bus.safety_score,
                                    "/100"
                                )
                            )}

                            ${detailItem(
                                "Condition",
                                bus.condition
                            )}

                            ${detailItem(
                                "Manufacturing Year",
                                bus.manufacturing_year
                            )}

                            ${detailItem(
                                "Bus Age",
                                formatValue(
                                    bus.bus_age,
                                    " years"
                                )
                            )}

                            ${detailItem(
                                "Last Inspection",
                                bus.last_inspection
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            📋 Fitness Certificate
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Fitness Status",
                                bus.fitness_status
                            )}

                            ${detailItem(
                                "Fitness Expiry",
                                bus.fitness_expiry
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            📄 Permit Information
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Permit Status",
                                bus.permit_status
                            )}

                            ${detailItem(
                                "Permit Expiry",
                                bus.permit_expiry
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            🛡️ Insurance Information
                        </h3>

                        <div class="details-grid">

                            ${detailItem(
                                "Insurance Status",
                                bus.insurance_status
                            )}

                            ${detailItem(
                                "Insurance Expiry",
                                bus.insurance_expiry
                            )}

                        </div>

                    </div>

                    <div class="details-section">

                        <h3>
                            👨‍✈️ Driver Information
                        </h3>

                        ${createStaffCard(
                            bus.driver,
                            "👨‍✈️",
                            "Driver"
                        )}

                    </div>

                    <div class="details-section">

                        <h3>
                            🎫 Conductor Information
                        </h3>

                        ${createStaffCard(
                            bus.conductor,
                            "🎫",
                            "Conductor"
                        )}

                    </div>

                </div>

            </div>
        `;

        document.body.appendChild(
            modal
        );

        const closeButton =
            modal.querySelector(
                "#closeBusDetails"
            );

        if (closeButton) {

            closeButton.addEventListener(
                "click",
                () => {
                    closeBusDetailsModal(
                        modal
                    );
                }
            );
        }

        const overlay =
            modal.querySelector(
                ".bus-details-overlay"
            );

        if (overlay) {

            overlay.addEventListener(
                "click",
                event => {

                    if (
                        event.target === overlay
                    ) {
                        closeBusDetailsModal(
                            modal
                        );
                    }

                }
            );
        }

        const escapeHandler =
            event => {

                if (
                    event.key === "Escape"
                ) {

                    if (
                        document.body.contains(
                            modal
                        )
                    ) {
                        closeBusDetailsModal(
                            modal
                        );
                    }

                    document.removeEventListener(
                        "keydown",
                        escapeHandler
                    );
                }
            };

        document.addEventListener(
            "keydown",
            escapeHandler
        );

    } catch (error) {

        console.error(
            "Bus details failed:",
            error
        );

        alert(
            `Unable to load details for ${busNumber}.\n\n${error.message}`
        );

    } finally {

        if (button) {

            button.disabled = false;

            button.innerHTML =
                button.dataset.originalText ||
                "View Full Details →";
        }
    }
}


/* ============================================================
   DETAIL ITEM
============================================================ */

function detailItem(
    label,
    value,
    extraClass = ""
) {
    const displayValue =
        value === undefined ||
        value === null ||
        value === ""
            ? "Not available"
            : String(value);

    return `
        <div class="details-item">

            <span>
                ${escapeHtml(label)}
            </span>

            <strong class="${escapeHtml(extraClass)}">
                ${escapeHtml(displayValue)}
            </strong>

        </div>
    `;
}


/* ============================================================
   STAFF CARD
============================================================ */

function createStaffCard(
    staff,
    icon,
    role
) {
    if (
        !staff ||
        typeof staff !== "object"
    ) {

        return `
            <div class="staff-card">

                <div class="staff-icon">
                    ${icon}
                </div>

                <div class="staff-information">

                    <strong>
                        ${escapeHtml(role)}
                    </strong>

                    <span>
                        Information not available
                    </span>

                </div>

            </div>
        `;
    }

    const name =
        staff.name ||
        "Not available";

    const experience =
        staff.experience ||
        "Not available";

    const rating =
        staff.rating !== undefined &&
        staff.rating !== null
            ? `⭐ ${staff.rating}/5`
            : "Rating not available";

    return `
        <div class="staff-card">

            <div class="staff-icon">
                ${icon}
            </div>

            <div class="staff-information">

                <strong>
                    ${escapeHtml(name)}
                </strong>

                <span>
                    Experience:
                    ${escapeHtml(experience)}
                </span>

                <span>
                    Rating:
                    ${escapeHtml(rating)}
                </span>

            </div>

        </div>
    `;
}


/* ============================================================
   FORMAT VALUE
============================================================ */

function formatValue(
    value,
    suffix = "",
    prefix = ""
) {
    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        return "Not available";
    }

    return `${prefix}${value}${suffix}`;
}


/* ============================================================
   CLOSE MODAL
============================================================ */

function closeBusDetailsModal(modal) {

    if (
        modal &&
        document.body.contains(
            modal
        )
    ) {
        modal.remove();
    }
}


/* ============================================================
   AI ASSISTANT
============================================================ */

function setupAI() {

    const sendButton =
        document.getElementById(
            "aiSend"
        );

    const input =
        document.getElementById(
            "aiQuestion"
        );

    if (!sendButton || !input) {
        return;
    }

    sendButton.addEventListener(
        "click",
        sendAIQuestion
    );

    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendAIQuestion();
            }

        }
    );

    document
        .querySelectorAll(
            ".ai-suggestion"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const question =
                        button.dataset.question ||
                        button.textContent.trim();

                    input.value =
                        question;

                    sendAIQuestion();
                }
            );

        });
}


/* ============================================================
   SEND AI QUESTION
============================================================ */

async function sendAIQuestion() {

    const input =
        document.getElementById(
            "aiQuestion"
        );

    const messages =
        document.getElementById(
            "aiMessages"
        );

    if (!input || !messages) {
        return;
    }

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    addAIMessage(
        message,
        true
    );

    input.value = "";

    try {

        const data =
            await apiFetch(
                "/assistant",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

        addAIMessage(
            data?.response ||
            "Sorry, I could not understand that.",
            false
        );

    } catch (error) {

        console.error(
            "AI assistant error:",
            error
        );

        addAIMessage(
            "The Smart Bus assistant is currently unavailable. Please check the backend.",
            false
        );
    }
}


/* ============================================================
   ADD AI MESSAGE
============================================================ */

function addAIMessage(
    message,
    isUser
) {

    const container =
        document.getElementById(
            "aiMessages"
        );

    if (!container) {
        return;
    }

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        isUser
            ? "ai-message ai-user"
            : "ai-message ai-bot";

    if (isUser) {

        wrapper.innerHTML = `
            <div class="ai-message-content">

                <strong>
                    You
                </strong>

                <p>
                    ${escapeHtml(message)}
                </p>

            </div>
        `;

    } else {

        wrapper.innerHTML = `
            <div class="ai-avatar">
                🤖
            </div>

            <div class="ai-message-content">

                <strong>
                    Smart Bus AI
                </strong>

                <p>
                    ${escapeHtml(message)}
                </p>

            </div>
        `;
    }

    container.appendChild(
        wrapper
    );

    container.scrollTop =
        container.scrollHeight;
}


/* ============================================================
   EXPENSES
============================================================ */

async function loadExpenses() {

    try {

        const data =
            await apiFetch(
                "/expenses"
            );

        const weekly =
            document.getElementById(
                "weeklyExpense"
            );

        const monthly =
            document.getElementById(
                "monthlyExpense"
            );

        const average =
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

        if (weekly) {
            weekly.textContent =
                `₹${data?.weekly ?? 0}`;
        }

        if (monthly) {
            monthly.textContent =
                `₹${data?.monthly ?? 0}`;
        }

        if (average) {
            average.textContent =
                `₹${data?.average ?? 0}`;
        }

        if (weeklyTrips) {
            weeklyTrips.textContent =
                `${data?.trips ?? 0} trips`;
        }

        if (monthlyTrips) {
            monthlyTrips.textContent =
                `${(data?.trips ?? 0) * 4} trips`;
        }

    } catch (error) {

        console.error(
            "Expense loading failed:",
            error
        );
    }
}


/* ============================================================
   HISTORY
============================================================ */

async function loadHistory() {

    const container =
        document.getElementById(
            "travelHistory"
        );

    if (!container) {
        return;
    }

    try {

        const data =
            await apiFetch(
                "/history"
            );

        const history =
            Array.isArray(data)
                ? data
                : Array.isArray(
                    data?.history
                )
                    ? data.history
                    : [];

        if (!history.length) {

            container.innerHTML = `
                <div class="status-card">

                    <div class="status-icon">
                        📋
                    </div>

                    <h2>
                        No journeys yet
                    </h2>

                    <p>
                        Your future bus journeys
                        will appear here.
                    </p>

                </div>
            `;

            return;
        }

        container.innerHTML =
            history
                .map(item => {

                    return `
                        <div class="history-card">

                            <div class="history-bus">

                                <div class="history-bus-icon">
                                    🚌
                                </div>

                                <div>

                                    <strong>
                                        ${escapeHtml(
                                            item?.bus
                                        )}
                                    </strong>

                                    <span>
                                        ${escapeHtml(
                                            item?.date
                                        )}
                                    </span>

                                </div>

                            </div>

                            <div class="history-route">

                                <span>
                                    ${escapeHtml(
                                        item?.route
                                    )}
                                </span>

                            </div>

                            <div class="history-fare">

                                <strong>
                                    ₹${escapeHtml(
                                        item?.fare
                                    )}
                                </strong>

                                <span>
                                    BUS FARE
                                </span>

                            </div>

                        </div>
                    `;
                })
                .join("");

    } catch (error) {

        console.error(
            "History loading failed:",
            error
        );

        container.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    ⚠️
                </div>

                <h2>
                    History unavailable
                </h2>

                <p>
                    Unable to load travel history.
                </p>

            </div>
        `;
    }
}


/* ============================================================
   CLEAR BUTTONS
============================================================ */

function setupClearButtons() {

    const clearFrom =
        document.getElementById(
            "clearFrom"
        );

    const clearTo =
        document.getElementById(
            "clearTo"
        );

    if (clearFrom) {

        clearFrom.addEventListener(
            "click",
            () => {

                const input =
                    document.getElementById(
                        "from"
                    );

                if (input) {

                    input.value = "";

                    input.focus();
                }
            }
        );
    }

    if (clearTo) {

        clearTo.addEventListener(
            "click",
            () => {

                const input =
                    document.getElementById(
                        "to"
                    );

                if (input) {

                    input.value = "";

                    input.focus();
                }
            }
        );
    }
}


/* ============================================================
   SWAP LOCATIONS
============================================================ */

function setupSwapButton() {

    const button =
        document.getElementById(
            "swapButton"
        );

    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        () => {

            const from =
                document.getElementById(
                    "from"
                );

            const to =
                document.getElementById(
                    "to"
                );

            if (!from || !to) {
                return;
            }

            const temporary =
                from.value;

            from.value =
                to.value;

            to.value =
                temporary;
        }
    );
}


/* ============================================================
   HTML ESCAPE
============================================================ */

function escapeHtml(value) {

    return String(
        value === undefined ||
        value === null
            ? ""
            : value
    )
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}
/* ============================================================
   AUTHORITY DASHBOARD - STEP 1
============================================================ */

function updateAuthorityDashboard(buses) {

    const activeBuses =
        document.getElementById("authorityActiveBuses");

    const monitored =
        document.getElementById("authorityMonitored");

    const crowd =
        document.getElementById("authorityCrowd");

    const lastUpdate =
        document.getElementById("authorityLastUpdate");

    const fleetList =
        document.getElementById("authorityFleetList");

    if (!activeBuses || !fleetList) {
        return;
    }

    const validBuses = Array.isArray(buses)
        ? buses
        : [];

    activeBuses.textContent = validBuses.length;

    if (monitored) {
        monitored.textContent = validBuses.length;
    }

    const crowdValues = validBuses
        .map(bus => Number(bus?.crowd))
        .filter(value => Number.isFinite(value));

    const averageCrowd =
        crowdValues.length
            ? Math.round(
                crowdValues.reduce(
                    (sum, value) => sum + value,
                    0
                ) / crowdValues.length
            )
            : 0;

    if (crowd) {
        crowd.textContent = `${averageCrowd}%`;
    }

    if (lastUpdate) {
        lastUpdate.textContent =
            `Updated ${new Date().toLocaleTimeString()}`;
    }

    if (!validBuses.length) {

        fleetList.innerHTML = `
            <div class="status-card">
                <p>No buses currently available.</p>
            </div>
        `;

        return;
    }

    fleetList.innerHTML = validBuses
        .map(bus => {

            return `
                <div class="authority-fleet-item">

                    <div class="authority-bus-info">

                        <strong>
                            🚌 ${escapeHtml(bus.number)}
                        </strong>

                        <span>
                            ${escapeHtml(bus.route)}
                        </span>

                        <span>
                            📍 ${escapeHtml(bus.location)}
                        </span>

                    </div>

                    <div class="authority-bus-metrics">

                        <span>
                            ${escapeHtml(bus.eta)} min
                        </span>

                        <span>
                            ${escapeHtml(bus.crowd)}%
                        </span>

                    </div>

                </div>
            `;

        })
        .join("");
}
/* ============================================================
   AI INCIDENT DETECTION - STEP 2
============================================================ */

let simulatedIncidents = [];
/* ============================================================
   STEP 5 - URBAN INTELLIGENCE & ANALYTICS
============================================================ */

let incidentHistory = [];

try {
    incidentHistory =
        JSON.parse(
            localStorage.getItem("smartBusIncidentHistory") || "[]"
        );
} catch {
    incidentHistory = [];
}


/* ============================================================
   STEP 5 - SAVE INCIDENT HISTORY
============================================================ */

function saveIncidentHistory() {

    try {

        localStorage.setItem(
            "smartBusIncidentHistory",
            JSON.stringify(
                incidentHistory.slice(0, 50)
            )
        );

    } catch (error) {

        console.error(
            "Incident history save failed:",
            error
        );
    }
}


/* ============================================================
   STEP 5 - ANALYTICS DASHBOARD
============================================================ */

function renderUrbanAnalytics() {

    const incidentContainer =
        document.getElementById(
            "authorityIncidentList"
        );

    if (!incidentContainer) {
        return;
    }

    let analytics =
        document.getElementById(
            "urbanAnalyticsDashboard"
        );

    if (!analytics) {

        analytics =
            document.createElement("div");

        analytics.id =
            "urbanAnalyticsDashboard";

        incidentContainer.parentNode.insertBefore(
            analytics,
            incidentContainer
        );
    }

    const incidents =
        Array.isArray(incidentHistory)
            ? incidentHistory
            : [];

    const total =
        incidents.length;

    const potholes =
        incidents.filter(incident =>
            String(incident.type)
                .toLowerCase()
                .includes("pothole")
        ).length;

    const congestion =
        incidents.filter(incident =>
            String(incident.type)
                .toLowerCase()
                .includes("congestion")
        ).length;

    const hazards =
        incidents.filter(incident =>
            String(incident.type)
                .toLowerCase()
                .includes("hazard")
        ).length;

    const resolved =
        incidents.filter(
            incident =>
                incident.status === "Resolved"
        ).length;

    const active =
        total - resolved;

    const busPerformance = {};

    incidents.forEach(incident => {

        const bus =
            incident.bus || "Unknown";

        if (!busPerformance[bus]) {

            busPerformance[bus] = {
                total: 0,
                resolved: 0
            };
        }

        busPerformance[bus].total++;

        if (
            incident.status === "Resolved"
        ) {
            busPerformance[bus].resolved++;
        }
    });

    const busRows =
        Object.entries(busPerformance)
            .slice(0, 5)
            .map(([bus, data]) => {

                const resolutionRate =
                    data.total
                        ? Math.round(
                            (
                                data.resolved /
                                data.total
                            ) * 100
                        )
                        : 0;

                return `
                    <div
                        style="
                            display:flex;
                            justify-content:space-between;
                            gap:12px;
                            padding:12px 0;
                            border-bottom:1px solid rgba(128,128,128,.15);
                        "
                    >

                        <strong>
                            🚌 ${escapeHtml(bus)}
                        </strong>

                        <span>
                            ${data.total} incidents
                            • ${resolutionRate}% resolved
                        </span>

                    </div>
                `;
            })
            .join("");

    const historicalRows =
        incidents
            .slice(0, 7)
            .map(incident => {

                return `
                    <div
                        style="
                            display:grid;
                            grid-template-columns:1fr 1fr 1fr;
                            gap:10px;
                            padding:9px 0;
                            border-bottom:1px solid rgba(128,128,128,.12);
                            font-size:13px;
                        "
                    >

                        <span>
                            ${escapeHtml(incident.type)}
                        </span>

                        <span>
                            🚌 ${escapeHtml(incident.bus)}
                        </span>

                        <span>
                            ${escapeHtml(incident.time)}
                        </span>

                    </div>
                `;
            })
            .join("");

    const maxCount =
        Math.max(
            potholes,
            congestion,
            hazards,
            1
        );

    function analyticsBar(
        label,
        value,
        icon
    ) {

        const width =
            Math.round(
                (value / maxCount) * 100
            );

        return `
            <div style="margin-bottom:14px;">

                <div
                    style="
                        display:flex;
                        justify-content:space-between;
                        margin-bottom:5px;
                    "
                >

                    <span>
                        ${icon} ${label}
                    </span>

                    <strong>
                        ${value}
                    </strong>

                </div>

                <div
                    style="
                        height:8px;
                        background:rgba(128,128,128,.15);
                        border-radius:20px;
                        overflow:hidden;
                    "
                >

                    <div
                        style="
                            width:${width}%;
                            height:100%;
                            background:currentColor;
                            border-radius:20px;
                            transition:width .4s ease;
                        "
                    ></div>

                </div>

            </div>
        `;
    }

    analytics.innerHTML = `

        <div
            style="
                margin:20px 0;
                padding:22px;
                border-radius:18px;
                border:1px solid rgba(128,128,128,.18);
                background:rgba(128,128,128,.04);
            "
        >

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:15px;
                    margin-bottom:20px;
                    flex-wrap:wrap;
                "
            >

                <div>

                    <div
                        style="
                            font-size:12px;
                            letter-spacing:1.5px;
                            font-weight:700;
                        "
                    >
                        URBAN INTELLIGENCE
                    </div>

                    <h2 style="margin:5px 0;">
                        📊 City Incident Analytics
                    </h2>

                    <p style="margin:0; opacity:.7;">
                        AI-powered overview of detected
                        bus network problems.
                    </p>

                </div>

                <div
                    style="
                        padding:8px 12px;
                        border-radius:20px;
                        background:rgba(0,150,100,.12);
                        font-size:13px;
                    "
                >
                    🟢 AI MONITORING ACTIVE
                </div>

            </div>


            <!-- INCIDENT SUMMARY -->

            <div
                style="
                    display:grid;
                    grid-template-columns:
                        repeat(auto-fit,minmax(130px,1fr));
                    gap:12px;
                    margin-bottom:22px;
                "
            >

                <div class="status-card">
                    <div class="status-icon">🚨</div>
                    <h2>${total}</h2>
                    <p>Total Incidents</p>
                </div>

                <div class="status-card">
                    <div class="status-icon">🕳️</div>
                    <h2>${potholes}</h2>
                    <p>Potholes</p>
                </div>

                <div class="status-card">
                    <div class="status-icon">🚦</div>
                    <h2>${congestion}</h2>
                    <p>Congestion</p>
                </div>

                <div class="status-card">
                    <div class="status-icon">🚧</div>
                    <h2>${hazards}</h2>
                    <p>Road Hazards</p>
                </div>

                <div class="status-card">
                    <div class="status-icon">🔥</div>
                    <h2>${active}</h2>
                    <p>Active Problems</p>
                </div>

            </div>


            <!-- PROBLEM ANALYSIS -->

            <div
                style="
                    display:grid;
                    grid-template-columns:
                        repeat(auto-fit,minmax(260px,1fr));
                    gap:20px;
                "
            >

                <div>

                    <h3>
                        🔥 Problem Area Analysis
                    </h3>

                    ${analyticsBar(
                        "Potholes",
                        potholes,
                        "🕳️"
                    )}

                    ${analyticsBar(
                        "Traffic Congestion",
                        congestion,
                        "🚦"
                    )}

                    ${analyticsBar(
                        "Road Hazards",
                        hazards,
                        "🚧"
                    )}

                    <p
                        style="
                            font-size:12px;
                            opacity:.65;
                            margin-top:15px;
                        "
                    >
                        Higher incident concentration
                        indicates a potential problem area.
                    </p>

                </div>


                <!-- INCIDENT VISUALIZATION -->

                <div>

                    <h3>
                        🗺️ Incident Visualization
                    </h3>

                    <div
                        style="
                            min-height:150px;
                            border-radius:14px;
                            padding:18px;
                            background:
                                radial-gradient(
                                    circle at 30% 40%,
                                    rgba(255,80,80,.35),
                                    transparent 18%
                                ),
                                radial-gradient(
                                    circle at 65% 60%,
                                    rgba(255,170,0,.30),
                                    transparent 20%
                                ),
                                rgba(128,128,128,.08);
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            text-align:center;
                        "
                    >

                        <div>

                            <div
                                style="
                                    font-size:35px;
                                    margin-bottom:8px;
                                "
                            >
                                🗺️
                            </div>

                            <strong>
                                AI Incident Heatmap Concept
                            </strong>

                            <p
                                style="
                                    margin:6px 0 0;
                                    font-size:12px;
                                    opacity:.7;
                                "
                            >
                                Incident markers on the live
                                map represent emerging
                                problem areas.
                            </p>

                        </div>

                    </div>

                </div>

            </div>


            <!-- BUS PERFORMANCE -->

            <div style="margin-top:25px;">

                <h3>
                    🚌 Bus / Route Performance
                </h3>

                ${
                    busRows ||
                    `
                        <p style="opacity:.65;">
                            Bus performance data will appear
                            as incidents are detected.
                        </p>
                    `
                }

            </div>


            <!-- HISTORICAL INFORMATION -->

            <div style="margin-top:25px;">

                <h3>
                    📈 Historical Incident Information
                </h3>

                ${
                    historicalRows ||
                    `
                        <p style="opacity:.65;">
                            Historical incidents will appear
                            here automatically.
                        </p>
                    `
                }

            </div>


            <!-- SYSTEM STATUS -->

            <div
                style="
                    margin-top:20px;
                    padding-top:15px;
                    border-top:1px solid rgba(128,128,128,.15);
                    display:flex;
                    justify-content:space-between;
                    flex-wrap:wrap;
                    gap:10px;
                    font-size:12px;
                    opacity:.7;
                "
            >

                <span>
                    Active incidents: ${active}
                </span>

                <span>
                    Resolved incidents: ${resolved}
                </span>

                <span>
                    Stored history: ${incidents.length}
                </span>

            </div>

        </div>
    `;
}


function generateAIIncident(buses) {

    if (!Array.isArray(buses) || !buses.length) {
        return null;
    }

    const bus =
        buses[
            Math.floor(
                Math.random() * buses.length
            )
        ];

    const incidents = [
        {
            type: "🕳️ Pothole Detected",
            confidence: 92
        },
        {
            type: "🚧 Road Hazard Detected",
            confidence: 88
        },
        {
            type: "🚦 Traffic Congestion Detected",
            confidence: 95
        }
    ];

    const incident =
        incidents[
            Math.floor(
                Math.random() * incidents.length
            )
        ];

    return {
        id: Date.now(),

        type: incident.type,

        confidence: incident.confidence,

        bus: bus.number || "Unknown Bus",

        location:
            bus.location ||
            "Location unavailable",

            latitude: Number(bus.latitude),

    longitude: Number(bus.longitude),


        time:
            new Date().toLocaleTimeString()
         
    };
}


function renderAIIncidents() {

    const container =
        document.getElementById(
            "authorityIncidentList"
        );

    if (!container) {
        return;
    }

    if (!simulatedIncidents.length) {

        container.innerHTML = `
            <div class="authority-empty-state">

                <div>🤖</div>

                <strong>
                    AI monitoring active
                </strong>

                <span>
                    No incidents detected yet.
                </span>

            </div>
        `;

        return;
    }

    container.innerHTML =
        simulatedIncidents
            .slice(0, 5)
            .map(incident => {

                return `
                    <div class="ai-incident-card">

                        <div class="ai-detection-label">
                            AI DETECTION
                        </div>

                        <div class="ai-incident-top">

                            <span class="ai-incident-type">
                                ${escapeHtml(
                                    incident.type
                                )}
                            </span>

                            <span class="ai-confidence">
                                ${escapeHtml(
                                    incident.confidence
                                )}% confidence
                            </span>

                        </div>

                        <div class="ai-incident-details">

                            <span>
                                🚌 Bus:
                                ${escapeHtml(
                                    incident.bus
                                )}
                            </span>

                            <span>
                                📍 Location:
                                ${escapeHtml(
                                    incident.location
                                )}
                            </span>

                        </div>

                        <div class="ai-incident-time">
                            Detected at
                            ${escapeHtml(
                                incident.time
                            )}
                        </div>

                    </div>
                `;

            })
            .join("");
}


function simulateAIIncidentDetection(buses) {

    const incident =
        generateAIIncident(buses);

    if (!incident) {
        return;
    }

    simulatedIncidents.unshift(
        incident
    );

    simulatedIncidents =
        simulatedIncidents.slice(0, 10);
        incidentHistory.unshift({
    ...incident,
    status: incident.status || "Detected"
});

incidentHistory =
    incidentHistory.slice(0, 50);

saveIncidentHistory();

    const incidentCount =
        document.getElementById(
            "authorityIncidents"
        );

    if (incidentCount) {
        incidentCount.textContent =
            simulatedIncidents.length;
    }

    renderAIIncidents();
    updateAIIncidentMarkers();
    renderAuthorityIncidents();
}


/* ============================================================
   START AI SIMULATION
============================================================ */

setInterval(async () => {

    try {

        const data =
            await apiFetch("/live-buses");

        const buses =
            Array.isArray(data?.buses)
                ? data.buses
                : [];

        if (buses.length) {
            simulateAIIncidentDetection(
                buses
            );
        }

    } catch (error) {

        console.error(
            "AI incident simulation failed:",
            error
        );

    }

}, 10000);
/* ============================================================
   AI INCIDENT MAP MARKERS - STEP 3
============================================================ */

function updateAIIncidentMarkers() {

    if (!mapInitialized || !busMap) {
        return;
    }

    simulatedIncidents.forEach(incident => {

        const latitude =
            Number(incident.latitude);

        const longitude =
            Number(incident.longitude);

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude)
        ) {
            return;
        }

        if (incidentMarkers[incident.id]) {
            return;
        }

        const popup = `
            <div class="smart-bus-popup">

                <div class="map-popup-title">
                    🚨 AI INCIDENT
                </div>

                <div class="map-popup-route">
                    ${escapeHtml(incident.type)}
                </div>

                <div class="map-popup-row">
                    <span>Bus</span>
                    <strong>
                        ${escapeHtml(incident.bus)}
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Location</span>
                    <strong>
                        ${escapeHtml(incident.location)}
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Confidence</span>
                    <strong>
                        ${escapeHtml(incident.confidence)}%
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>GPS</span>
                    <strong>
                        ${latitude.toFixed(5)},
                        ${longitude.toFixed(5)}
                    </strong>
                </div>

                <div class="map-popup-row">
                    <span>Detected</span>
                    <strong>
                        ${escapeHtml(incident.time)}
                    </strong>
                </div>

            </div>
        `;

        const marker =
            L.circleMarker(
                [latitude, longitude],
                {
                    radius: 9,
                    className: "ai-incident-map-marker"
                }
            )
            .addTo(busMap)
            .bindPopup(popup);

        incidentMarkers[incident.id] = marker;
    });
}
/* ============================================================
   STEP 4 - AUTHORITY INCIDENT MANAGEMENT
============================================================ */

function renderAuthorityIncidents() {

    const container =
        document.getElementById(
            "authorityIncidentList"
        );

    if (!container) {
        return;
    }

    if (
        typeof simulatedIncidents === "undefined" ||
        !Array.isArray(simulatedIncidents) ||
        !simulatedIncidents.length
    ) {
        container.innerHTML = `
            <div class="status-card">

                <div class="status-icon">
                    🛡️
                </div>

                <h2>
                    No incidents to manage
                </h2>

                <p>
                    AI-detected incidents will appear here.
                </p>

            </div>
        `;

        return;
    }

    container.innerHTML =
        simulatedIncidents
            .map(createAuthorityIncidentCard)
            .join("");
}


/* ============================================================
   AUTHORITY INCIDENT CARD
============================================================ */

function createAuthorityIncidentCard(incident) {

    const status =
        incident.status || "Detected";

    const statusClass =
        getIncidentStatusClass(status);

    return `
        <div class="authority-incident-card">

            <div class="authority-incident-top">

                <div class="authority-incident-type">
                    🚨 ${escapeHtml(incident.type)}
                </div>

                <span
                    class="authority-incident-status ${statusClass}"
                >
                    ${escapeHtml(status)}
                </span>

            </div>

            <div class="authority-incident-details">

                <div class="authority-detail">
                    <span>Bus</span>
                    <strong>
                        ${escapeHtml(incident.bus)}
                    </strong>
                </div>

                <div class="authority-detail">
                    <span>Location</span>
                    <strong>
                        ${escapeHtml(incident.location)}
                    </strong>
                </div>

                <div class="authority-detail">
                    <span>Confidence</span>
                    <strong>
                        ${escapeHtml(incident.confidence)}%
                    </strong>
                </div>

                <div class="authority-detail">
                    <span>Time</span>
                    <strong>
                        ${escapeHtml(incident.time)}
                    </strong>
                </div>

            </div>

            <div class="authority-incident-actions">

                ${createIncidentActionButton(
                    incident,
                    "Verified"
                )}

                ${createIncidentActionButton(
                    incident,
                    "Assigned"
                )}

                ${createIncidentActionButton(
                    incident,
                    "In Progress"
                )}

                ${createIncidentActionButton(
                    incident,
                    "Resolved"
                )}

            </div>

        </div>
    `;
}


/* ============================================================
   INCIDENT ACTION BUTTON
============================================================ */

function createIncidentActionButton(
    incident,
    newStatus
) {

    if (
        incident.status === newStatus
    ) {
        return "";
    }

    return `
        <button
            type="button"
            class="authority-action-button"
            onclick="updateIncidentStatus(
                ${incident.id},
                '${newStatus}'
            )"
        >
            ${escapeHtml(newStatus)}
        </button>
    `;
}


/* ============================================================
   UPDATE INCIDENT STATUS
============================================================ */

function updateIncidentStatus(
    incidentId,
    newStatus
) {

    if (
        typeof simulatedIncidents === "undefined"
    ) {
        return;
    }

    const incident =
        simulatedIncidents.find(
            item =>
                Number(item.id) ===
                Number(incidentId)
        );

    if (!incident) {
        return;
    }

    incident.status = newStatus;
    const historicalIncident =
    incidentHistory.find(
        item =>
            Number(item.id) ===
            Number(incidentId)
    );

if (historicalIncident) {

    historicalIncident.status =
        newStatus;

    saveIncidentHistory();
}

    renderAIIncidents();

    renderAuthorityIncidents();

    updateAIIncidentMarkers();
}


/* ============================================================
   INCIDENT STATUS CLASS
============================================================ */

function getIncidentStatusClass(status) {

    switch (status) {

        case "Verified":
            return "incident-status-verified";

        case "Assigned":
            return "incident-status-assigned";

        case "In Progress":
            return "incident-status-progress";

        case "Resolved":
            return "incident-status-resolved";

        default:
            return "incident-status-detected";
    }
}
/* ============================================================
   STEP 5 - START URBAN ANALYTICS
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        /*
         * Render analytics after the page
         * and existing dashboard are ready.
         */
        setTimeout(() => {

            renderUrbanAnalytics();

        }, 500);

    }
);


/* ============================================================
   STEP 5 - UPDATE ANALYTICS AUTOMATICALLY
============================================================ */

setInterval(() => {

    renderUrbanAnalytics();

}, 2000);
function toggleProfileMenu() {
    const menu = document.getElementById("profileDropdown");

    if (menu) {
        menu.classList.toggle("show");
    }
}

document.addEventListener("click", function(event) {

    const profileMenu = document.querySelector(".profile-menu");
    const dropdown = document.getElementById("profileDropdown");

    if (
        profileMenu &&
        dropdown &&
        !profileMenu.contains(event.target)
    ) {
        dropdown.classList.remove("show");
    }

});