document.addEventListener('DOMContentLoaded', async function () {
    await fetchBoatData();
    renderMonths();
    setupMap();

});

let monthlyBoatData = {};

async function fetchBoatData() {
    try {
        const response = await fetch('/api/boat');
        monthlyBoatData = await response.json();
        const totals = calculateTotals(monthlyBoatData);
//        console.log('Calculated totals:', totals);
        updateInfoBox(totals);
    } catch (error) {
        console.error('Error fetching boat data:', error);
    }
}

function calculateTotals(data) {
    return {
        arriving: {
            Container: sumByKey(data.arriving, 'Container'),
            "Dry Bulk": sumByKey(data.arriving, 'Dry Bulk'),
            Passenger: sumByKey(data.arriving, 'Passenger')
        },
        departing: {
            Container: sumByKey(data.departing, 'Container'),
            "Dry Bulk": sumByKey(data.departing, 'Dry Bulk'),
            Passenger: sumByKey(data.departing, 'Passenger')
        }
    };
}

function sumByKey(data, key) {
    return Object.values(data).reduce((acc, item) => acc + (item[key] || 0), 0);
}

function renderMonths() {
    const months = get12Months();
    const monthListElement = document.querySelector('.timeline .month-list');

    monthListElement.innerHTML = months.map((month, index) => {
        const formattedMonth = formatMonth(month);
        return `<li class="month-item" data-index="${index}" data-month="${formattedMonth}">${month.substring(5)}</li>`;
    }).join('');

    document.querySelectorAll('.month-item').forEach(item => {
        item.addEventListener('mouseover', function () {
            showTooltip(this.dataset.index);
        });
    });
}

function get12Months() {
    const result = [];
    const currentDate = new Date();
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    for (let i = 11; i >= 0; i--) {
        const d = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
        result.push(`${d.getFullYear()}-${monthNames[d.getMonth()]}`);
    }
    return result;
}

function formatMonth(month) {
    const monthNames = { Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06", Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12" };
    const parts = month.split('-');
    const year = parts[0];
    const monthNumber = monthNames[parts[1]];
    return `${year}-${monthNumber}-01`;
}

function initializePage() {
    selectedArriving = true;
    selectedDeparting = true;

    const arrivingShips = { getLayers: () => selectedArriving ? [{}] : [] };
    const departingShips = { getLayers: () => selectedDeparting ? [{}] : [] };

    updateSelection(arrivingShips, departingShips);
    updateInfoBox();
}

function updateSelection(arrivingShips, departingShips) {
    selectedArriving = arrivingShips.getLayers().length > 0;
    selectedDeparting = departingShips.getLayers().length > 0;
    updateSelection(arrivingShips, departingShips);  // Update selection state only
}

function updateInfoBox(totals = { arriving: { Container: 0, "Dry Bulk": 0, Passenger: 0 }, departing: { Container: 0, "Dry Bulk": 0, Passenger: 0 } }) {
//    console.log('Updating info box', totals);

    const finalTotals = {
        Container: totals.arriving.Container + totals.departing.Container,
        "Dry Bulk": totals.arriving["Dry Bulk"] + totals.departing["Dry Bulk"],
        Passenger: totals.arriving.Passenger + totals.departing.Passenger
    };
//    console.log('Final totals for animation:', finalTotals);

    const duration = 6300; // Duration of the animation in milliseconds
    const frameRate = 120; // Frames per second
    const frames = duration / (1000 / frameRate);
    let currentFrame = 0;

    let startValues = { Container: 0, "Dry Bulk": 0, Passenger: 0 };

    function animateFrame() {
        const progress = currentFrame / frames;
        startValues.Container = Math.floor(finalTotals.Container * progress);
        startValues["Dry Bulk"] = Math.floor(finalTotals["Dry Bulk"] * progress);
        startValues.Passenger = Math.floor(finalTotals.Passenger * progress);

        document.querySelectorAll('.boat-count')[0].textContent = `貨櫃船: ${startValues.Container}`;
        document.querySelectorAll('.boat-count')[1].textContent = `乾散貨船: ${startValues["Dry Bulk"]}`;
        document.querySelectorAll('.boat-count')[2].textContent = `客船: ${startValues.Passenger}`;

        currentFrame++;

        if (currentFrame <= frames) {
            requestAnimationFrame(animateFrame);
        } else {
            document.querySelectorAll('.boat-count')[0].textContent = `貨櫃船: ${finalTotals.Container}`;
            document.querySelectorAll('.boat-count')[1].textContent = `乾散貨船: ${finalTotals["Dry Bulk"]}`;
            document.querySelectorAll('.boat-count')[2].textContent = `客船: ${finalTotals.Passenger}`;
        }
    }

    animateFrame();
}

function showTooltip(index) {
    const tooltip = document.getElementById('tooltip');
    const monthItem = document.querySelector(`.month-item[data-index="${index}"]`);
    const selectedMonth = monthItem.dataset.month;
    const formattedMonth = formatMonth(selectedMonth);

    let containerCount = 0;
    let dryBulkCount = 0;
    let passengerCount = 0;

    if (selectedArriving) {
        const arrivingData = monthlyBoatData.arriving?.[selectedMonth] || {};
        containerCount += arrivingData.Container || 7630;
        dryBulkCount += arrivingData["Dry Bulk"] || 3620;
        passengerCount += arrivingData.Passenger || 380;
    }

    if (selectedDeparting) {
        const departingData = monthlyBoatData.departing?.[selectedMonth] || {};
        containerCount += departingData.Container || 1;
        dryBulkCount += departingData["Dry Bulk"] || 2;
        passengerCount += departingData.Passenger || 3;
    }

    const tooltipContent = `
        <p class="tooltip-text">貨櫃船: ${containerCount}</p>
        <p class="tooltip-text">乾散貨船: ${dryBulkCount}</p>
        <p class="tooltip-text">客船: ${passengerCount}</p>
    `;

    tooltip.innerHTML = tooltipContent;

    const rect = monthItem.getBoundingClientRect();
    const tooltipHeight = tooltip.offsetHeight;
    const yOffset = 10;

    const top = rect.top + window.scrollY - tooltipHeight - yOffset;
    const left = rect.left + window.scrollX + rect.width / 2 - tooltip.offsetWidth / 2;

    const finalTop = Math.max(0, top);
    const finalLeft = Math.min(Math.max(0, left), window.innerWidth - tooltip.offsetWidth);

    tooltip.style.top = `${finalTop}px`;
    tooltip.style.left = `${finalLeft}px`;

    tooltip.classList.add('visible');

    monthItem.addEventListener('mouseleave', function () {
        tooltip.classList.remove('visible');
    });
}

function setupMap() {
    const map = L.map('map', {
        center: [23.6978, 120.9605],
        zoom: 4,
        worldCopyJump: true,
        attributionControl: false
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &amp; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    const arrivingShips = L.featureGroup().addTo(map);
    const departingShips = L.featureGroup().addTo(map);

    const layerControl = L.control.layers(null, {
        '進港船舶': arrivingShips,
        '出港船舶': departingShips
    }, {
        collapsed: false
    }).addTo(map);

    layerControl.getContainer().addEventListener('change', function () {
        updateSelection(arrivingShips, departingShips);
    });

    const portCoordinates = {
        "TWKHH": [22.6178, 120.3067],
        "TWTPE": [25.0375, 121.5645],
        "TWKEL": [25.1307, 121.7415],
        "TWTXG": [24.1433, 120.5412]
    };

    const months = get12Months();
    animateShipsByMonths(months, arrivingShips, departingShips, portCoordinates, map);
}

function animateShipsByMonths(months, arrivingShips, departingShips, portCoordinates, map) {
    let currentMonthIndex = 0;

    function animateCurrentMonth() {
        if (currentMonthIndex >= months.length) return;

        fetch(`/api/port?month=${months[currentMonthIndex]}`)
            .then(response => response.json())
            .then(data => {
                arrivingShips.clearLayers();
                departingShips.clearLayers();

                data.features.forEach(feature => {
                    const props = feature.properties;
                    const geoCoords = feature.geometry.coordinates;
                    let startLatLng, endLatLng;

                    if (props.status === 'arriving') {
                        startLatLng = L.latLng(geoCoords[1], geoCoords[0]);
                        endLatLng = L.latLng(...portCoordinates[props.end_port]);
                    } else {
                        startLatLng = L.latLng(...portCoordinates[props.start_port]);
                        endLatLng = L.latLng(geoCoords[1], geoCoords[0]);
                    }

                    L.Marker.movingMarker([startLatLng, endLatLng], [6000], {
                        autostart: true,
                        loop: false,
                        icon: L.divIcon({
                            className: 'custom-div-icon',
                            html: "<div style='background-color:red;'></div>",
                            iconSize: [3, 3],
                            iconAnchor: [1.5, 1.5]
                        })
                    }).addTo(props.status === 'arriving' ? arrivingShips : departingShips);
                });

                currentMonthIndex++;
                if (currentMonthIndex < months.length) {
                    setTimeout(animateCurrentMonth, 6000); // Pause between months
                }
            })
            .catch(e => console.error(e));
    }

    startMonthIndicatorAnimation(62000);
    arrivingShips.addTo(map);
    departingShips.addTo(map);
    animateCurrentMonth();
}

// Start the month indicator animation
function startMonthIndicatorAnimation(duration) {
    const indicator = document.querySelector('.month-indicator');
    const monthItems = document.querySelectorAll('.timeline li');

    const firstMonthPosition = monthItems[0].offsetLeft + (monthItems[0].offsetWidth / 2);
    const lastMonthPosition = monthItems[monthItems.length - 1].offsetLeft + (monthItems[monthItems.length - 1].offsetWidth / 2);

    const totalDistance = lastMonthPosition - firstMonthPosition;
    const segmentDistance = totalDistance / 13;

    let startTime = null;
    let currentSegment = 0;

    function updatePosition(timestamp) {
        if (!startTime) startTime = timestamp;

        const elapsedTime = timestamp - startTime;
        const progress = elapsedTime / duration;
        const segmentProgress = (progress * 12) % 1;

        currentSegment = Math.floor(progress * 12);
        if (currentSegment > 12) currentSegment = 12;

        const currentLeftPosition = firstMonthPosition + segmentDistance * (currentSegment + segmentProgress);
        indicator.style.left = `${currentLeftPosition}px`;

        if (currentSegment < 12) {
            requestAnimationFrame(updatePosition);
        } else {
            indicator.style.left = `${firstMonthPosition + totalDistance}px`;
        }
    }
    requestAnimationFrame(updatePosition);
}
