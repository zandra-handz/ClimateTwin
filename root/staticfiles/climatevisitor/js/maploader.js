function displayMapAnimation(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var canvas = document.createElement('canvas'); // Create canvas element
    canvas.id = 'map-canvas'; // Set ID for canvas element
    canvas.width = resultContainer.offsetWidth; // Set canvas width
    canvas.height = resultContainer.offsetHeight; // Set canvas height
    resultContainer.appendChild(canvas);
    const dotContainer = resultContainer; // Assign dot container

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

        // Load map image
        mapImage.src = '{% static "climatevisitor/map1.PNG" %}';

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
    }

    // Call drawMap function to initiate drawing
    drawMap();

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
}
