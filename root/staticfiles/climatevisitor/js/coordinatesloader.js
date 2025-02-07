

function displayLoading(resultContainerId, user_token) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    //loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection 
     // local
     // const socket = new WebSocket(`ws://127.0.0.1:8000/ws/climate-twin/?user_token=${user_token}`);
 
    //const socket = new WebSocket(`wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/?user_token=${user_token}`);
    const socket = new WebSocket(`wss://climatetwin.com/ws/climate-twin/?user_token=${user_token}`);
 
    socket.onopen = function(event) {
        // console.log('displayLoading WebSocket connection opened');
    };
 
    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        replaceUpdate(update); 
    };

    // Event listener -- close
    socket.onclose = function(event) {
        // console.log('displayLoading WebSocket connection closed');
    };

    
    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function getColorFromIndex(index) {
    switch (index) {
        case 0: return 'red';
        case 1: return 'darkorange';
        case 2: return 'orange'; 
        case 3: return 'orangegold'; 
        case 4: return 'darkgreen';
        case 5: return 'blue'; 
        case 6: return 'darkblue';
        case 7: return 'purple';
        case 8: return 'purple';
        default: return 'black'; // Fallback to black if index is out of range
    }
}

function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    
    // In-line CSS  
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    // updateElement.style.paddingBottom = '32px'; 
 
    if (update.latitude !== undefined && update.longitude !== undefined) {
        const tempDifference = update.temp_difference;
    
        let color;
        if (tempDifference < 2) {
            // Map values less than 2 to colors from black to red
            const red = Math.floor(255 * (tempDifference / 2));
            color = `rgb(${red}, 0, 0)`;
        } else if (tempDifference <= 30) {
            // Map values between 2 and 50 to evenly distributed colors
            const colorIndex = Math.floor(((tempDifference - 2) / 28) * 8); // Adjusted to 8 colors between orange and purple
            color = getColorFromIndex(colorIndex);
        } else {
            // Black for temp difference greater than 50
            color = 'black';
        }
        
            // Create block-level elements for country name and temperature

            const countryBox = document.createElement('div');
            countryBox.textContent = `${update.country_name}`;
            countryBox.style.color = 'black'; // Set country name color
        
            const tempBox = document.createElement('div');
            tempBox.textContent = `${update.temperature}°`;
            tempBox.style.color = color; // Set temperature color
            // tempBox.style.fontWeight = '800';
            // tempBox.style.opacity = '0.2';
            // tempBox.style.transition = 'opacity 1s ease-out'; 
            
            // Get the map container element
            const mapContainer = document.getElementById('map-container');

            function setFontSize() {
                const containerHeight = mapContainer.clientHeight; // Get the height of the map container
                const fontSize = containerHeight / 5; // Calculate font size as 1/5 of container height
                tempBox.style.fontSize = fontSize + 'px'; // Set font size in pixels
            }

            setFontSize();

            /* 
            // Set the font size of tempBox based on the height of the map container
            function setFontSize() {
                const containerHeight = mapContainer.clientHeight; // Get the height of the map container
                const fontSize = containerHeight * 0.9; // Adjust 0.9 as necessary for your layout
                tempBox.style.fontSize = fontSize + 'px'; // Set font size in pixels
            }
            
            // Call setFontSize initially to set the initial font size
            setFontSize();

            // Add a resize event listener to update the font size when the map container's size changes
            window.addEventListener('resize', setFontSize);
            */
           
            // Function to set the top margin of tempBox based on the height of the map container
            function setMargin() {
                const containerHeight = mapContainer.clientHeight; // Get the height of the map container
                tempBox.style.marginTop = containerHeight + 'px'; // Set top margin in pixels
            }

            // Function to set the background color and radius behind text
            function setBackground() {
                const margin = mapContainer.clientHeight + 'px'; 
                tempBox.style.position = 'relative'; 
                tempBox.style.backgroundColor = '#FFF';  
                tempBox.style.padding = '8px';
                tempBox.style.borderRadius = '50%';
                tempBox.style.marginTop = margin;
            }

            setBackground();

            function handleResize() {
                setMargin();  
            }

            window.addEventListener('resize', handleResize);
                
            updateElement.innerHTML = '';
            updateElement.appendChild(tempBox);
            
            /*
            setTimeout(() => {
                tempBox.style.opacity = '0'; // Set opacity to 0 for fade out
            }, 600); // 3000 milliseconds = 3 seconds
            */

        // updateElement.innerHTML = `${update.country_name}, <span style="color: ${color}">${update.temperature}°</span>`;

        /*
    
        updateElement.textContent = `${update.country_name}, ${update.temperature}°, ${tempDifference} degrees off`;
        updateElement.style.color = color;
    
        
        updateElement.textContent = `Twin Finder is in ${update.country_name}, ${update.temperature}°, `; // ${update.latitude}, ${update.longitude}`;
        updateElement.style.color = 'black'; 

        
        if (update.latitude > 0) {
            updateElement.innerHTML += `<span style="color: green">${update.latitude}, </span>`;
        } else if (update.latitude < 0) {
            updateElement.innerHTML += `<span style="color: red">${update.latitude}, </span>`;
        } else {
            updateElement.innerHTML += `${update.latitude}, `;
        }

        if (update.longitude > 0) {
            updateElement.innerHTML += `<span style="color: blue">${update.longitude}</span>`;
        } else if (update.longitude < 0) {
            updateElement.innerHTML += `<span style="color: orange">${update.longitude}</span>`;
        } else {
            updateElement.innerHTML += `${update.longitude}`;
        }
        */
 
        if (update.last) {
            const loadingContainer = document.querySelector('.loading-container');
            if (loadingContainer) {
                loadingContainer.remove();  
            }
        }
    } else {
        const loadingContainer = document.querySelector('.loading-container');
        if (loadingContainer) {
            loadingContainer.remove();  
        }
    }

    container.innerHTML = '';  
    container.appendChild(updateElement);
}


function displayLocationUpdate(resultContainerId, user_token) { 
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    // loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);
 // local
    // const socket = new WebSocket(`ws://127.0.0.1:8000/ws/climate-twin/current/?user_token=${user_token}`);

   // const socket = new WebSocket(`wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/current/?user_token=${user_token}`);
    const socket = new WebSocket(`wss://climatetwin.com/ws/climate-twin/current/?user_token=${user_token}`);



    socket.onopen = function(event) {
        console.log('displayLocationUpdate WebSocket connection opened');
    };

    socket.onmessage = function(event) {
        const update = JSON.parse(event.data);
        locationUpdate(update); 
    };

    socket.onclose = function(event) {
        console.log('displayLocationUpdate WebSocket connection closed');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}



function locationUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    // updateElement.style.paddingBottom = '32px';
 
    if (update.latitude !== undefined && update.longitude !== undefined) { 
        const mapContainer = document.getElementById('map-container');
        mapContainer.innerHTML = ''; 
        mapContainer.style.display = 'none'; // Hide the map container
        
        updateElement.textContent = `You are in ${update.name}`;
        updateElement.style.color = 'black'; 
    } else { 
        updateElement.textContent = update.name;
        updateElement.style.color = 'black';
    }

    container.innerHTML = ''; 
    container.appendChild(updateElement);
}
