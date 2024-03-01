// Function to append new update to the container
function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    updateElement.textContent = `Latitude: ${update.latitude}, Longitude: ${update.longitude}`;
    container.innerHTML = ''; // Clear the container's content
    container.appendChild(updateElement);
}

// WebSocket connection
const socket = new WebSocket('ws://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL

// Event listener for WebSocket open
socket.onopen = function(event) {
    console.log('WebSocket connection opened');
};

// Event listener for WebSocket messages
socket.onmessage = function(event) {
    const update = JSON.parse(event.data);
    appendUpdate(update);
};

// Event listener for WebSocket close
socket.onclose = function(event) {
    console.log('WebSocket connection closed');
};

// Event listener for WebSocket errors
socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};
