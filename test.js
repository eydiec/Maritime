document.addEventListener('DOMContentLoaded', async () => {
    const boatData = await fetchBoatData();
    renderMonths();
    setupMap();
    updateInitialData(boatData);
});

async function fetchBoatData() {
    try {
        const response = await fetch('/api/boat');
        const data = await response.json();
        return processData(data);
    } catch (error) {
        console.error('Error fetching boat data:', error);
    }
}

function processData(data) {
    const totals = calculateTotals(data);
    updateInfoBox(totals);
    return data; // Return processed data for further use
}

function calculateTotals(data) {
    return {
        arriving: calculateByCategory(data.arriving),
        departing: calculateByCategory(data.departing),
    };
}

function calculateByCategory(categoryData) {
    return {
        Container: sumByKey(categoryData, 'Container'),
        "Dry Bulk": sumByKey(categoryData, 'Dry Bulk'),
        Passenger: sumByKey(categoryData, 'Passenger')
    };
}

function sumByKey(data, key) {
    return Object.values(data).reduce((total, item) => total + (item[key] || 0), 0);
}

function renderMonths() {
    const months = get12Months();
    const monthList = document.querySelector('.timeline .month-list');
    monthList.innerHTML = months.map((month, index) => createMonthItem(month, index)).join('');
    addMonthHoverListeners();
}

function createMonthItem(month, index) {
    const formattedMonth = formatMonth(month);
    return `<li class="month-item" data-index="${index}" data-month="${formattedMonth}">${month.substring(5)}</li>`;
}

function addMonthHoverListeners() {
    document.querySelectorAll('.month-item').forEach(item => {
        item.addEventListener('mouseover', () => showTooltip(item.dataset.index));
    });
}

function updateInitialData(boatData) {
    // Function to perform any initial data updates or animations on page load
    animateInitialData(boatData);
}

function setupMap() {
    const map = initializeMap();
    const {arrivingShips, departingShips} = setupShipLayers(map);
    configureLayerControl(map, arrivingShips, departingShips);
}

function initializeMap() {
    // Map initialization code
}

function setupShipLayers(map) {
    // Ship layer setup code
}

function configureLayerControl(map, arrivingShips, departingShips) {
    // Layer control configuration code
}
