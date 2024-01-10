$(document).ready(function() {
    $.get('/generate', function(data) {
        $('#map-container').html(data);
    });
});