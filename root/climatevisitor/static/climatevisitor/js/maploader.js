// maploader.js

// Function to display map animation
function displayMapAnimation(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var canvas = document.createElement('canvas'); // Create canvas element
    canvas.id = 'map-canvas'; // Set ID for canvas element
    resultContainer.appendChild(canvas);

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

function updateAnimation(update) {
    // Define maximum latitude and longitude values
    const maxLatitude = 90; // Maximum latitude value on Earth
    const maxLongitude = 180; // Maximum longitude value on Earth

    const canvas = document.getElementById('map-canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas

    // Draw map (if needed)
    // Your code to draw map

    // Draw dots based on latitude and longitude
    const latitude = parseFloat(update.latitude);
    const longitude = parseFloat(update.longitude);
    const dotSize = 5; // Size of the dots
    const dotColor = 'red'; // Color of the dots

    ctx.fillStyle = dotColor;
    for (let i = 0; i < latitude.length; i++) {
        // Map latitude and longitude values to coordinates on the canvas
        const x = (longitude[i] + 180) * (canvas.width / 360);
        const y = (90 - latitude[i]) * (canvas.height / 180);

        ctx.beginPath();
        ctx.arc(x, y, dotSize, 0, Math.PI * 2);
        ctx.fill();
    }


    // Draw a constant dot at a fixed position
    const constantDotX = 100; // X coordinate of the constant dot
    const constantDotY = 100; // Y coordinate of the constant dot
    const constantDotSize = 10; // Size of the constant dot
    const constantDotColor = 'blue'; // Color of the constant dot

    ctx.fillStyle = constantDotColor;
    ctx.beginPath();
    ctx.arc(constantDotX, constantDotY, constantDotSize, 0, Math.PI * 2);
    ctx.fill();
}

}
