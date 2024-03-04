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
    //const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');

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
    
    // Apply CSS styles to center, make it smaller, and add padding
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    updateElement.style.paddingBottom = '5px'; // Adjust the value as needed

    // Change font color based on coordinates or display completed message
    if (update.latitude !== undefined && update.longitude !== undefined) {
        // Setting the search text to black
        updateElement.textContent = `Searching ${update.latitude}, ${update.longitude}`;
        updateElement.style.color = 'black'; 

        // Change font color based on coordinates
        if (update.latitude > 0) {
            updateElement.innerHTML += `<br>Latitude: <span style="color: green">${update.latitude}</span>`;
        } else if (update.latitude < 0) {
            updateElement.innerHTML += `<br>Latitude: <span style="color: red">${update.latitude}</span>`;
        } else {
            updateElement.innerHTML += `<br>Latitude: ${update.latitude}`;
        }

        if (update.longitude > 0) {
            updateElement.innerHTML += `, Longitude: <span style="color: blue">${update.longitude}</span>`;
        } else if (update.longitude < 0) {
            updateElement.innerHTML += `, Longitude: <span style="color: orange">${update.longitude}</span>`;
        } else {
            updateElement.innerHTML += `, Longitude: ${update.longitude}`;
        }
    } else {
        // Display completed message if no coordinates left
        updateElement.textContent = 'Completed';
        updateElement.style.color = 'gray';

        // Fade out and remove the message after 5 seconds
        const fadeOutDuration = 2000; // 2 seconds
        const fadeOutInterval = 20; // 20 milliseconds
        const initialOpacity = 1;

        let opacity = initialOpacity;
        const intervalId = setInterval(() => {
            opacity -= (1 / (fadeOutDuration / fadeOutInterval));
            updateElement.style.opacity = opacity;
            if (opacity <= 0) {
                clearInterval(intervalId);
                updateElement.remove();
            }
        }, fadeOutInterval);
    }

    container.innerHTML = '';  
    container.appendChild(updateElement);
}
