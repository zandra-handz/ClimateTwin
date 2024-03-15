

function displayLoading(resultContainerId, user_token) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    //loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // WebSocket connection
    //const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    // const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/');
     // Construct WebSocket URL with query parameter
    const socket = new WebSocket(`wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/?user_token=${user_token}`);
 
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


function replaceUpdate(update) {
    const container = document.getElementById('climate-updates-container');
    const updateElement = document.createElement('div');
    
    // In-line CSS  
    updateElement.style.textAlign = 'center';
    updateElement.style.fontSize = 'small';
    // updateElement.style.paddingBottom = '32px'; 
 
    if (update.latitude !== undefined && update.longitude !== undefined) { 
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


function displayLocationUpdate(resultContainerId) {
    var resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-container');
    // loadingDiv.innerHTML = '<div class="spinner"></div>';
    resultContainer.appendChild(loadingDiv);

    // const socket = new WebSocket('wss://localhost:8000/ws/climate-twin/'); // Replace with your WebSocket URL
    const socket = new WebSocket('wss://climatetwin-lzyyd.ondigitalocean.app/ws/climate-twin/current/');

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
        
        updateElement.textContent = `You are in ${update.name}`;
        updateElement.style.color = 'black'; 
    } else { 
        updateElement.textContent = update.name;
        updateElement.style.color = 'black';
    }

    container.innerHTML = ''; 
    container.appendChild(updateElement);
}
