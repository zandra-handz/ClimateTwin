function displayMapAnimation(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var canvas = document.createElement('canvas'); // Create canvas element
    canvas.id = 'map-canvas'; // Set ID for canvas element
    resultContainer.appendChild(canvas);
    canvas.width = resultContainer.offsetWidth; // Set canvas width
    canvas.height = resultContainer.offsetHeight; // Set canvas height
    const dotContainer = resultContainer; // Assign dot container as the canvas itself

    // WebSocket connection
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

    function drawMap() {
        // Get canvas context
        const ctx = canvas.getContext('2d');
        
        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    
        // Draw a simple map background
        // ctx.fillStyle = 'lightblue';
        // ctx.fillRect(0, 0, canvas.width, canvas.height);
    
        // Draw some example features (e.g., rivers, mountains, cities)
        // You can use various canvas drawing functions (e.g., arc, lineTo, fillText) to draw the map features
        // Example:
        // ctx.fillStyle = 'green';
        // ctx.fillRect(100, 100, 50, 50); // Draw a green rectangle representing a forest
    }

    // Call drawMap function to initiate drawing
    drawMap();
    // Function to update animation with latitude and longitude
    function updateAnimation(update) {
        const latitude = parseFloat(update.latitude);
        const longitude = parseFloat(update.longitude);
        createDot(latitude, longitude);
    }// Keep track of the currently displayed dot
    let currentDot = null;

    function createDot(latitude, longitude) {
        const dot = document.createElement('div');
        dot.classList.add('dot');

        // Convert latitude and longitude to screen coordinates
        const x = (longitude + 180) * (canvas.offsetWidth / 360);
        const y = (90 - latitude) * (canvas.offsetHeight / 180);

        // Check if the calculated coordinates are within the canvas bounds
        if (x < 0 || x > canvas.width || y < 0 || y > canvas.height) {
            console.error('Dot coordinates are outside the canvas bounds.');
            return; // Exit the function if coordinates are outside bounds
        }

        // Set dot initial position
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';

        // Append dot to the dot container
        dotContainer.appendChild(dot);

        // If there's a current dot, start the fade-out animation for it
        if (currentDot) {
            currentDot.style.opacity = '0';
            // Remove the dot from the DOM after fading out
            setTimeout(() => {
                dotContainer.removeChild(currentDot);
            }, 260); // Adjust this value for the fade-out duration
        }

        // Set the new dot as the current dot
        currentDot = dot;
    }
}

/*
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
    const dotSize = 2; // Size of the dots
    const dotColor = 'red'; // Color of the dots

    ctx.fillStyle = dotColor;

    // Map latitude and longitude values to coordinates on the canvas
    const x = (longitude + 180) * (canvas.width / 360);
    const y = (90 - latitude) * (canvas.height / 180);

    ctx.beginPath();
    ctx.arc(x, y, dotSize, 0, Math.PI * 2);
    ctx.fill();

    // Draw a constant dot at a fixed position
    const constantDotX = 100; // X coordinate of the constant dot
    const constantDotY = 100; // Y coordinate of the constant dot
    const constantDotSize = 2; // Size of the constant dot
    const constantDotColor = 'blue'; // Color of the constant dot

    ctx.fillStyle = constantDotColor;
    ctx.beginPath();
    ctx.arc(constantDotX, constantDotY, constantDotSize, 0, Math.PI * 2);
    ctx.fill();
}
}    */