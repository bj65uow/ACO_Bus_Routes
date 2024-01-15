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

    // Update the GET request URL to include arrays of values
    xhr.open('GET', '/generate_routes?start_node=' + startArray.join('&start_node=') + '&end_node=' + endArray.join('&end_node='), true);
    xhr.send();
}