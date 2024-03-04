// coordinatesloader.js


function displayLoading(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    //loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection
    //const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');

    // Event listener -- open
    socket.onopen = function(event) {
        console.log('WebSocket connection opened');
    };

    // Event listener -- messages
    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        replaceUpdate(update); 
    };

    // Event listener -- close
    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
    };

    // Event listener -- errors
    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

// Function to append new update to the container
function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    updateElement.textContent = `Searching ${update.latitude}, ${update.longitude}`;
    
    // Apply CSS styles to center and make it smaller
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';

    // Change font color based on coordinates
    if (update.latitude > 0) {
        updateElement.style.color = 'green'; // Change to whatever color you prefer
    } else if (update.latitude < 0) {
        updateElement.style.color = 'red'; // Change to whatever color you prefer
    }

    if (update.longitude > 0) {
        updateElement.style.color = 'blue'; // Change to whatever color you prefer
    } else if (update.longitude < 0) {
        updateElement.style.color = 'orange'; // Change to whatever color you prefer
    }

    container.innerHTML = '';  
    container.appendChild(updateElement);
}
