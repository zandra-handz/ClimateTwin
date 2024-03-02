// spinner.js

// Function to display loading spinner and fetch socket data
function displayLoading(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    // Clear existing content
    resultContainer.innerHTML = '';
    // Create a div to contain the spinner
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    // Add the spinner inside the div
    loadingDiv.innerHTML = '<div class="spinner"></div>';
    // Append the loading div to the result container
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection
    //const socket = new WebSocket('ws://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    const socket = new WebSocket('ws://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');
    // Event listener for WebSocket open
    socket.onopen = function(event) {
        console.log('WebSocket connection opened');
    };

    // Event listener for WebSocket messages
    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        replaceUpdate(update); // Call replaceUpdate to display the socket output
    };

    // Event listener for WebSocket close
    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
    };

    // Event listener for WebSocket errors
    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

// Function to append new update to the container
function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    updateElement.textContent = `Latitude: ${update.latitude}, Longitude: ${update.longitude}`;
    container.innerHTML = ''; // Clear the container's content
    container.appendChild(updateElement);
}

