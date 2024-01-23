function newMap() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('map-container').innerHTML = xhr.responseText;
        }
    };
    xhr.open('GET', '/generate_stops', true);
    xhr.send();
}

function updateMap() {
    // Get number of ants and iterations from the settings menu
    var numAnts = document.getElementById('num_ants').value;
    var numIterations = document.getElementById('num_iterations').value;
    
    // Get the selected mode from the radio buttons
    var mode;
    var modeRadioButtons = document.getElementsByName('mode');
    for (var i = 0; i < modeRadioButtons.length; i++) {
        if (modeRadioButtons[i].checked) {
            mode = modeRadioButtons[i].value;
            break;
        }
    }

    // Get all pairs of values
    var startValues = document.querySelectorAll('input[name^="start_node[]"]');
    var endValues = document.querySelectorAll('input[name^="end_node[]"]');

    // Create arrays to store values
    var startArray = [];
    var endArray = [];

    // Populate arrays with values
    startValues.forEach(function(element) {
        startArray.push(encodeURIComponent(element.value));
    });

    endValues.forEach(function(element) {
        endArray.push(encodeURIComponent(element.value));
    });

    // Create the GET request with arrays of values
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('map-container').innerHTML = xhr.responseText;
        }
    };

    // Update the GET request URL to include arrays of values, ants, and iterations
    xhr.open('GET', '/generate_routes?start_node=' + startArray.join('&start_node=') + '&end_node=' + endArray.join('&end_node=') + '&num_ants=' + numAnts + '&num_iterations=' + numIterations + '&mode=' + mode, true);
    xhr.send();
}

function addBusStop() {
    // Clone the bus stop template and increment the ID
    var busStopTemplate = document.querySelector('.bus_stop');
    var newBusStop = busStopTemplate.cloneNode(true);
    var currentId = parseInt(newBusStop.id);
    newBusStop.id = (currentId + 1).toString();

    // Reset input values
    newBusStop.querySelector('.start_node').value = '';
    newBusStop.querySelector('.end_node').value = '';

    // Append the new bus stop to the container
    document.getElementById('bus_stops').appendChild(newBusStop);
}

function removeLastBusStop() {
    var busStopsContainer = document.getElementById('bus_stops');
    var lastBusStop = busStopsContainer.lastElementChild;

    // Only remove if there is more than one bus stop
    if (busStopsContainer.childElementCount > 1) {
        busStopsContainer.removeChild(lastBusStop);
    }
}