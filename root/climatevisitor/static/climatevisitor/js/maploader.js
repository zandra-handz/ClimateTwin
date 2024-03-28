function displayMapAnimation(mapContainerId) {
   
    
    function setMapContainerHeight() {
        const mapContainer = document.getElementById(mapContainerId);
        const width = mapContainer.offsetWidth;
        const height = width / 2; 
        mapContainer.style.height = height + 'px';
    }

    
    setMapContainerHeight();

    window.addEventListener('resize', setMapContainerHeight);

    const mapContainer = document.getElementById(mapContainerId);
    mapContainer.innerHTML = ''; 

    const mapCanvas = document.createElement('canvas');
    mapCanvas.id = 'map-canvas';
    mapContainer.appendChild(mapCanvas);

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
    
        const x = (longitude + 180) * (mapCanvas.offsetWidth / 360);
        const y = (90 - latitude) * (mapCanvas.offsetHeight / 180);
    
        if (x < 0 || x > mapCanvas.offsetWidth || y < 0 || y > mapCanvas.offsetHeight) {
            console.error('Dot coordinates are outside the canvas bounds.');
            return; 
        }
    
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';
    
        mapContainer.appendChild(dot);
    
        setTimeout(() => {
            if (dot.parentNode === mapContainer) { 
                mapContainer.removeChild(dot);
            }
        }, 600); 
    
        const previousDot = mapContainer.querySelector('.dot.current');
        if (previousDot) {
            previousDot.style.opacity = 0; 
            
            setTimeout(() => {
                if (previousDot.parentNode === mapContainer) {
                    mapContainer.removeChild(previousDot);
                }
            }, 100); 
        }
    
        dot.classList.add('current');
    }
    
    
    /*
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
        }, 800); // Adjust this value as needed
    
        // Fade out the previous dot, if any
        const previousDot = mapContainer.querySelector('.dot.current');
        if (previousDot) {
            previousDot.style.opacity = 0; // Set opacity to 0 to trigger fade-out
            // Remove the dot after a short delay
            setTimeout(() => {
                mapContainer.removeChild(previousDot);
            }, 180); // Adjust this value for the fade-out duration
        }
    
        // Set the new dot as the current dot
        dot.classList.add('current');
    }
    */
    
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

    
    window.addEventListener('resize', () => handleResize(mapContainer));

    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');

    socket.onopen = function(event) {
        console.log('WebSocket connection opened');
    };

    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        updateAnimation(update);
    };

    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    // Call the function to draw the center dot initially
    //drawCenterDot(mapContainer);
}

function displayMapUpdate(mapContainerId) {
    var mapContainer = document.getElementById(mapContainerId);
    mapContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    // loadingDiv.innerHTML = '<div class="spinner"></div>';
    mapContainer.appendChild(loadingDiv);

    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/current/');

    socket.onopen = function(event) {
        console.log('displayMapUpdate WebSocket connection opened');
    };

    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        mapUpdate(update); 
    };

    socket.onclose = function(event) {
        console.log('displayMapUpdate WebSocket connection closed');
    };

    socket.onerror = function(error) {
        console.error('displayMapUpdate WebSocket error:', error);
    };
}

function mapUpdate(update) {
    const mapContainer = document.getElementById('map-container');
    const mapCanvas = document.createElement('canvas');
    mapCanvas.id = 'map-canvas';
    mapContainer.innerHTML = '';
    mapContainer.appendChild(mapCanvas);

    mapCanvas.width = mapContainer.offsetWidth;
    mapCanvas.height = mapContainer.offsetHeight;

    const latitude = parseFloat(update.latitude);
    const longitude = parseFloat(update.longitude);

    // Check if there are any dots in the map container
    const dots = mapContainer.querySelectorAll('.current-dot');
    if (dots.length > 0) {
        createPulsingDot(latitude, longitude, mapContainer);

        // Remove the map container after five seconds
        // This is getting called each time the websocket initially connects
        setTimeout(() => {
            mapContainer.parentNode.removeChild(mapContainer);
        }, 5000);
    } 
}



function createPulsingDot(latitude, longitude, mapContainer) {
    const dot = document.createElement('div');
    dot.classList.add('current-dot');
    dot.classList.add('pulsing');

    const x = (longitude + 180) * (mapContainer.offsetWidth / 360);
    const y = (90 - latitude) * (mapContainer.offsetHeight / 180);

    dot.style.left = x + 'px';
    dot.style.top = y + 'px';

    mapContainer.appendChild(dot);

    setTimeout(() => {
        mapContainer.removeChild(dot);
    }, 3000);
}





