function displayMapAnimation(mapContainerId) {
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

        // Set dot initial position
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';

        // Append dot to the dot container
        mapContainer.appendChild(dot);

        // Fade out the previous dot
        const currentDot = mapContainer.querySelector('.dot.current');
        if (currentDot) {
            currentDot.classList.remove('current');
            setTimeout(() => {
                mapContainer.removeChild(currentDot);
            }, 1000); // Adjust this value for the fade-out duration
        }

        // Set the new dot as the current dot
        dot.classList.add('current');
    }

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
    }

    function handleResize(mapContainer) {
        // Remove the previous center dot, if exists
        const previousCenterDot = mapContainer.querySelector('.center-dot');
        if (previousCenterDot) {
            mapContainer.removeChild(previousCenterDot);
        }
        
        // Redraw the center dot
        drawCenterDot(mapContainer);
    
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
    drawCenterDot(mapContainer);
}