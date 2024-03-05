// maploader.js

// maploader.js

function displayMapAnimation(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var canvas = document.createElement('canvas'); // Create canvas element
    canvas.id = 'map-canvas'; // Set ID for canvas element
    resultContainer.appendChild(canvas);
    //const canvas = document.getElementById('map-canvas');
    const dotContainer = document.getElementById('map-container');


    function drawMap() {
        const mapImage = new Image();
        const ctx = canvas.getContext('2d');

        // Set up onload event handler for the image
        mapImage.onload = function() {
            // Once the image is loaded, draw it onto the canvas
            ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
        };

        // Set up error handler for the image loading
        mapImage.onerror = function() {
            console.error('Failed to load the map image.');
        };

        
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

    }
    }

// Function to update animation with latitude and longitude
function updateAnimation(update) {
    const latitude = parseFloat(update.latitude);
    const longitude = parseFloat(update.longitude);
    createDot(latitude, longitude);
}

// Function to create a dot with trailing fade-out effect
function createDot(latitude, longitude) {
    const dot = document.createElement('div');
    dot.classList.add('dot');

    // Convert latitude and longitude to screen coordinates
    const x = (longitude + 180) * (canvas.offsetWidth / 360);
    const y = (90 - latitude) * (canvas.offsetHeight / 180);

    // Set dot initial position
    dot.style.left = x + 'px';
    dot.style.top = y + 'px';

    dotContainer.appendChild(dot);

    // Start the fade-out animation after a delay
    setTimeout(() => {
        dot.style.opacity = '0';
        // Remove the dot from the DOM after fading out
        setTimeout(() => {
            dotContainer.removeChild(dot);
        }, 260); // Adjust this value for the fade-out duration
    }, 100); // Adjust this value for the delay before fading out
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