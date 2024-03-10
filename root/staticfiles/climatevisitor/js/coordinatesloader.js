// coordinatesloader.js

function displayLoading(resultContainerId, user_token) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    //loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection
    //const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    // const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');
     // Construct WebSocket URL with query parameter
    const socket = new WebSocket(`wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/?user_token=${user_token}`);

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

/*
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
*/

// Function to append new update to the container
function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    
    // Apply CSS styles to center, make it smaller, and add padding
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    updateElement.style.paddingBottom = '32px'; // Adjust the value as needed
 
    if (update.latitude !== undefined && update.longitude !== undefined) { 
        updateElement.textContent = `Twin Finder is searching in ${update.country_name}`; // ${update.latitude}, ${update.longitude}`;
        updateElement.style.color = 'black'; 
 
        if (update.latitude > 0) {
            updateElement.innerHTML += `<br>Lat: <span style="color: green">${update.latitude}</span>`;
        } else if (update.latitude < 0) {
            updateElement.innerHTML += `<br>Lat: <span style="color: red">${update.latitude}</span>`;
        } else {
            updateElement.innerHTML += `<br>Lat: ${update.latitude}`;
        }

        if (update.longitude > 0) {
            updateElement.innerHTML += `, Long: <span style="color: blue">${update.longitude}</span>`;
        } else if (update.longitude < 0) {
            updateElement.innerHTML += `, Long: <span style="color: orange">${update.longitude}</span>`;
        } else {
            updateElement.innerHTML += `, Long: ${update.longitude}`;
        }

        // Check if it's the last update
        if (update.last) {
            const loadingContainer = document.querySelector('.loading-container');
            if (loadingContainer) {
                loadingContainer.remove(); // Remove the loading container
            }
        }
    } else {
        // Display completed message if no coordinates left
        updateElement.textContent = 'Completed';
        updateElement.style.color = 'gray';
    }

    container.innerHTML = '';  
    container.appendChild(updateElement);
}




function displayLocationUpdate(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    //loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection
    //const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/current/');

    // Event listener -- open
    socket.onopen = function(event) {
        console.log('WebSocket connection opened');
    };

    // Event listener -- messages
    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        locationUpdate(update); 
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
function locationUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    container.innerHTML = '';
    const updateElement = document.createElement('div');
    
    // Apply CSS styles to center, make it smaller, and add padding
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    updateElement.style.paddingBottom = '32px'; // Adjust the value as needed
 
    if (update.latitude !== undefined && update.longitude !== undefined) { 
        updateElement.textContent = '';
        updateElement.textContent = `You are now in ${update.name}.`; // ${update.latitude}, ${update.longitude}`;
        updateElement.style.color = 'black'; 
        /*
        if (update.latitude > 0) {
            updateElement.innerHTML += `<br>Lat: <span style="color: green">${update.latitude}</span>`;
        } else if (update.latitude < 0) {
            updateElement.innerHTML += `<br>Lat: <span style="color: red">${update.latitude}</span>`;
        } else {
            updateElement.innerHTML += `<br>Lat: ${update.latitude}`;
        }

        if (update.longitude > 0) {
            updateElement.innerHTML += `, Long: <span style="color: blue">${update.longitude}</span>`;
        } else if (update.longitude < 0) {
            updateElement.innerHTML += `, Long: <span style="color: orange">${update.longitude}</span>`;
        } else {
            updateElement.innerHTML += `, Long: ${update.longitude}`;
        } */
    } else {
        // Display completed message if no coordinates left
        updateElement.textContent = 'Completed';
        updateElement.style.color = 'gray';
    }

    container.innerHTML = '';
    container.appendChild(updateElement);
}