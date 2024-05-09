// Initialize data on page load
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
//        alert(JSON.stringify(monthlyBoatData, null, 2));
//        let totalArrivingContainers = sumByKey(monthlyBoatData.arriving, 'Container');
//        let totalDepartingContainers = sumByKey(monthlyBoatData.departing, 'Container');
//        let totalArrivingDrybulks = sumByKey(monthlyBoatData.arriving, 'Dry Bulk');
//        let totalDepartingDrybulks = sumByKey(monthlyBoatData.departing, 'Dry Bulk');
//        let totalArrivingPassengers = sumByKey(monthlyBoatData.arriving, 'Passenger');
//        let totalDepartingPassengers = sumByKey(monthlyBoatData.departing, 'Passenger');
        const totals = {
            arriving: {
                Container: sumByKey(monthlyBoatData.arriving, 'Container'),
                "Dry Bulk": sumByKey(monthlyBoatData.arriving, 'Dry Bulk'),
                Passenger: sumByKey(monthlyBoatData.arriving, 'Passenger')
            },
            departing: {
                Container: sumByKey(monthlyBoatData.departing, 'Container'),
                "Dry Bulk": sumByKey(monthlyBoatData.departing, 'Dry Bulk'),
                Passenger: sumByKey(monthlyBoatData.departing, 'Passenger')
            }
        };

        updateInfoBox(totals);


    } catch (error) {
        console.error('Error fetching boat data:', error);
    }
}

function sumByKey(data, key) {
    return Object.values(data).reduce((acc, item) => acc + (item[key] || 0), 0);
}


function formatMonth(month) {
    const monthNames = { Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06", Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12" };
    const parts = month.split('-'); // Split "2023-Aug" into ["2023", "Aug"]
    const year = parts[0];
    const monthNumber = monthNames[parts[1]]; // Convert "Aug" to "08"
    return `${year}-${monthNumber}-01`; // Format as "2023-08-01"
}

function renderMonths() {
    const months = get12Months();
    const monthListElement = document.querySelector('.timeline .month-list');

    monthListElement.innerHTML = months.map((month, index) =>
        {const formattedMonth = formatMonth(month); // Format "2023-Jun" to "2023-06-01"
        return `<li class="month-item" data-index="${index}" data-month="${formattedMonth}">${month.substring(5)}</li>`;}
//        `<li class="month-item" data-index="${index}" data-month="${month}">${month.substring(5)}</li>`
    ).join('');

    // mouseover event listeners to each month element
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

// once webpage opened, show totals with animation
document.addEventListener('DOMContentLoaded', function () {
    // Initial setup assuming both layers are meant to be selected on page load
    selectedArriving = true;
    selectedDeparting = true;

    // Mock layer objects to simulate layer selections
    const arrivingShips = { getLayers: () => selectedArriving ? [{}] : [] };
    const departingShips = { getLayers: () => selectedDeparting ? [{}] : [] };

    updateSelection(arrivingShips, departingShips);
    updateInfoBox();  // ensure the initial data is set up and animated
});

function updateSelection(arrivingShips, departingShips) {
    // whether arriving or departing layers are selected
    selectedArriving = arrivingShips.getLayers().length > 0;
    selectedDeparting = departingShips.getLayers().length > 0;

    // Update information based on selected layers
    updateInfoBox();
}


function updateInfoBox(totals) {

    // cumulative values
    const finalTotals = {
        Container: totals.arriving.Container + totals.departing.Container,
        "Dry Bulk": totals.arriving["Dry Bulk"] + totals.departing["Dry Bulk"],
        Passenger: totals.arriving.Passenger + totals.departing.Passenger
    };
//    alert(JSON.stringify(finalTotals, null, 2));
    // animation settings
    const duration = 6000; // seconds per month
    const frameRate = 120; // frames per second
    const frames = duration / (1000 / frameRate);
    let currentFrame = 0;

    // Starting values
    let startValues = { Container: 0, "Dry Bulk":0, Passenger: 0 };

    // Animation function
    function animateFrame() {
        // Calculate the increment based on the progress of the animation
        const progress = currentFrame / frames;
        startValues.Container = Math.floor(finalTotals.Container * progress);
        startValues["Dry Bulk"] = Math.floor(finalTotals["Dry Bulk"] * progress);
        startValues.Passenger = Math.floor(finalTotals.Passenger * progress);

        // Update infobox with current values
        document.querySelectorAll('.boat-count')[0].textContent = `貨櫃船: ${startValues.Container}`;
        document.querySelectorAll('.boat-count')[1].textContent = `乾散貨船: ${startValues["Dry Bulk"]}`;
        document.querySelectorAll('.boat-count')[2].textContent = `客船: ${startValues.Passenger}`;

        currentFrame++;

        // Continue animating until reaching the final frame
        if (currentFrame <= frames) {
            requestAnimationFrame(animateFrame);
        } else{
                // Ensure the final totals are accurately displayed
            document.querySelectorAll('.boat-count')[0].textContent = `貨櫃船: ${finalTotals.Container}`;
            document.querySelectorAll('.boat-count')[1].textContent = `乾散貨船: ${finalTotals["Dry Bulk"]}`;
            document.querySelectorAll('.boat-count')[2].textContent = `客船: ${finalTotals.Passenger}`;

        }
    }

    // Start the animation
    animateFrame();
}






function showTooltip(index) {
    const tooltip = document.getElementById('tooltip');
    const monthItem = document.querySelector(`.month-item[data-index="${index}"]`);
    const selectedMonth = monthItem.dataset.month; // "2023-Aug"
    const formattedMonth = formatMonth(selectedMonth); // "2023-08-01"

//    alert(formattedMonth); // formatted month
//    const monthData = monthlyBoatData.arriving[formattedMonth];
//    alert(JSON.stringify(monthData, null, 2));

    // Initialize the data variables
    let containerCount = 0;
    let dryBulkCount = 0;
    let passengerCount = 0;


    // Check if arriving ships are selected and add their counts
    if (selectedArriving) {
        const arrivingData = monthlyBoatData.arriving?.[selectedMonth] || {};
        containerCount += arrivingData.Container || 5330;
        dryBulkCount += arrivingData["Dry Bulk"] || 2830;
        passengerCount += arrivingData.Passenger || 280;
    }
    // Check if departing ships are selected and add their counts
    if (selectedDeparting) {
        const departingData = monthlyBoatData.departing?.[selectedMonth] || {};
        containerCount += departingData.Container || 1;
        dryBulkCount += departingData["Dry Bulk"] || 2;
        passengerCount += departingData.Passenger || 3;
    }
    // Construct the tooltip content dynamically
    let tooltipContent = `
        <p class="tooltip-text">貨櫃船: ${containerCount}</p>
        <p class="tooltip-text">乾散貨船: ${dryBulkCount}</p>
        <p class="tooltip-text">客船: ${passengerCount}</p>
    `;


    // Set the inner HTML of the tooltip
    tooltip.innerHTML = tooltipContent;


    // Position the tooltip above the hovered item
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
    var map = L.map('map', {
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

    var arrivingShips = L.featureGroup().addTo(map);
    var departingShips = L.featureGroup().addTo(map);

    var layerControl = L.control.layers(null, {
        '進港船舶': arrivingShips,
        '出港船舶': departingShips
    }, {
        collapsed: false
    }).addTo(map);

    // Update selection on layer changes
        layerControl.getContainer().addEventListener('change', function () {
            updateSelection(arrivingShips, departingShips);
        });

    const portCoordinates = {
            "TWKHH": [22.6178, 120.3067],
            "TWTPE": [25.0375, 121.5645],
            "TWKEL": [25.1307, 121.7415],
            "TWTXG": [24.1433, 120.5412]
        };



    function animateShipsByMonths(months) {
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

                        var movingMarker = L.Marker.movingMarker([startLatLng, endLatLng], [6000], {
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
                        setTimeout(animateCurrentMonth, 6000); // a pause between months

                    }
                 })
                .catch(e => console.error(e));
        }
        startMonthIndicatorAnimation(60000);

        arrivingShips.addTo(map);
        departingShips.addTo(map);



        animateCurrentMonth();
    }

    const months = get12Months();
    animateShipsByMonths(months);
}

function startMonthIndicatorAnimation(duration) {
    const indicator = document.querySelector('.month-indicator');
    const timeline = document.querySelector('.timeline ul');
    const totalMonths = 360; // adjusting the right position

    // Calculate the width of the timeline and the width per month segment
    const timelineWidth = timeline.offsetWidth;
    const monthWidth = timelineWidth / totalMonths;

    // Determine the starting month index from the current date
    const currentDate = new Date();
    let startMonth = currentDate.getMonth() ; //the last 12 months as starting point

    // Calculate initial left position based on starting month
    const initialLeftPosition = monthWidth * startMonth *8.5;
    indicator.style.left = `${initialLeftPosition}px`;

    // Define animation settings
    const startTime = Date.now();
    const endTime = startTime + duration;

    function updatePosition() {
        const currentTime = Date.now();
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1); // Ensures the progress does not exceed 1

        // Calculate new left position based on elapsed time
        const newLeftPosition = initialLeftPosition + (timelineWidth - initialLeftPosition) * progress;
        indicator.style.left = `${newLeftPosition}px`;

        if (currentTime < endTime) {
            requestAnimationFrame(updatePosition);
        } else {
            // Snap to the correct end position if there's any rounding error in calculations
            indicator.style.left = `${timelineWidth - monthWidth}px`;
        }
    }

    updatePosition();
}



