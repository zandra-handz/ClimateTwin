function displayMapAnimation(mapContainerId) {
    // Function to set the height of the map container
    function setMapContainerHeight() {
        const mapContainer = document.getElementById(mapContainerId);
        const width = mapContainer.offsetWidth;
        const height = width / 2; // Set height to half of the width
        mapContainer.style.height = height + 'px';
    }

    // Call the function to set the initial height on page load
    setMapContainerHeight();

    // Call the function whenever the window is resized
    window.addEventListener('resize', setMapContainerHeight);

    // Your existing displayMapAnimation function and other related functions go here...

    const mapContainer = document.getElementById(mapContainerId);
    mapContainer.innerHTML = ''; // Clear any existing content

    // Create canvas element
    const mapCanvas = document.createElement('canvas');
    mapCanvas.id = 'map-canvas';
    mapContainer.appendChild(mapCanvas);

    // Set canvas dimensions
    mapCanvas.width = mapContainer.offsetWidth;
    mapCanvas.height = mapContainer.offsetHeight;

    function updateAnimation(update) {
        const latitude = parseFloat(update.latitude);
        const longitude = parseFloat(update.longitude);
    
        // Add the new dot immediately
        createDot(latitude, longitude, mapContainer);
    }
    
    function createDot(latitude, longitude, mapContainer) {
        const dot = document.createElement('div');
        dot.classList.add('dot');
    
        // Convert latitude and longitude to screen coordinates
        const x = (longitude + 180) * (mapCanvas.offsetWidth / 360);
        const y = (90 - latitude) * (mapCanvas.offsetHeight / 180);
    
        // Check if the calculated coordinates are within the canvas bounds
        if (x < 0 || x > mapCanvas.offsetWidth || y < 0 || y > mapCanvas.offsetHeight) {
            console.error('Dot coordinates are outside the canvas bounds.');
            return; // Exit the function if coordinates are outside bounds
        }
    
        // Set dot position
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';
    
        // Append dot to the dot container
        mapContainer.appendChild(dot);
    
        // Remove the dot after a certain period (e.g., 5 seconds)
        setTimeout(() => {
            mapContainer.removeChild(dot);
        }, 5000); // Adjust this value as needed
    
        // Fade out the previous dot, if any
        const previousDot = mapContainer.querySelector('.dot.current');
        if (previousDot) {
            previousDot.style.opacity = 0; // Set opacity to 0 to trigger fade-out
            // Remove the dot after a short delay
            setTimeout(() => {
                mapContainer.removeChild(previousDot);
            }, 600); // Adjust this value for the fade-out duration
        }
    
        // Set the new dot as the current dot
        dot.classList.add('current');
    }
    
    /*
    function drawCenterDot(mapContainer) {
        const dot = document.createElement('div');
        dot.classList.add('center-dot');

        // Calculate latitude and longitude for the center of the map
        const centerLatitude = 0;
        const centerLongitude = 0;

        // Convert latitude and longitude to screen coordinates
        const x = (centerLongitude + 180) * (mapCanvas.offsetWidth / 360);
        const y = (90 - centerLatitude) * (mapCanvas.offsetHeight / 180);

        // Set dot position
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';

        // Append dot to the dot container
        mapContainer.appendChild(dot);
    } */

    function handleResize(mapContainer) {
        // Remove the previous center dot, if exists
        /*
        const previousCenterDot = mapContainer.querySelector('.center-dot');
        if (previousCenterDot) {
            mapContainer.removeChild(previousCenterDot);
        }
        
        // Redraw the center dot
        drawCenterDot(mapContainer);
        */
        // Recalculate and update positions of all dots
        const dotElements = mapContainer.querySelectorAll('.dot');
        dotElements.forEach(dotElement => {
            const latitude = parseFloat(dotElement.dataset.latitude);
            const longitude = parseFloat(dotElement.dataset.longitude);
            createDot(latitude, longitude, mapContainer);
        });
    }

    // Event listener for window resize
    window.addEventListener('resize', () => handleResize(mapContainer));

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

    // Call the function to draw the center dot initially
    //drawCenterDot(mapContainer);
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