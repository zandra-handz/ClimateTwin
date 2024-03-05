// maploader.js

// Function to display map animation
function displayMapAnimation(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('map-canvas');
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
        updateAnimation(update); 
    };

    // Event listener -- close
    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
    };

    // Event listener -- errors
    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    // Function to update animation
    function updateAnimation(update) {
        const canvas = document.getElementById('map-container');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
        
        // Draw map (if needed)
        // Your code to draw map
        
        // Draw dots based on latitude and longitude
        const latitude = update.latitude;
        const longitude = update.longitude;
        const dotSize = 5; // Size of the dots
        const dotColor = 'red'; // Color of the dots

        ctx.fillStyle = dotColor;
        for (let i = 0; i < latitude.length; i++) {
            ctx.beginPath();
            ctx.arc(longitude[i], latitude[i], dotSize, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}
