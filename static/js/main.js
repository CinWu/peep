$( document ).ready(function() {
    $("#approve").on('click', function() {

	$("#approve").remove();
	$("#reject").remove();
	var button="<button type='button' class='btn-xs btn-success disabled'>Approved</button>";
	$("#notifs").append(button);
	
	data = $('#notifs').serialize();
	data += "&status=approve"
	$.ajax({
	    url: "/",
            data: data,
	    type: "POST"
        });    
    });

    $("#reject").on('click', function() {
	$("#approve").remove();
	$("#reject").remove();
	var button="<button type='button' class='btn-xs btn-danger disabled'>Rejected</button>";
	$("#notifs").append(button);

	data = $('#notifs').serialize();
	data += "&status=reject"
	$.ajax({
	    url: "/",
            data: data,
	    type: "POST"
        });  
    });
});

var geocoder;
var map;
function initialize() {
    geocoder = new google.maps.Geocoder();
    var mapOptions = {
	zoom: 14,
	panControl: false,
	zoomControl: false,
	scaleControl: true
    };
    map = new google.maps.Map(document.getElementById('map-canvas'),
			      mapOptions);

    // Try HTML5 geolocation
    if(navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(function(position) {
	    var pos = new google.maps.LatLng(position.coords.latitude,
					     position.coords.longitude);

	    var marker = new google.maps.Marker({
		position: pos,
		map: map,
		draggable: true,
	    });

	    map.setCenter(pos);
	}, function() {
	    handleNoGeolocation(true);
	});
    } else {
	// Browser doesn't support Geolocation
	handleNoGeolocation(false);
    }
}

function handleNoGeolocation(errorFlag) {
    if (errorFlag) {
	var content = 'Error: The Geolocation service failed.';
    } else {
	var content = 'Error: Your browser doesn\'t support geolocation.';
    }

    var options = {
	map: map,
	position: new google.maps.LatLng(60, 105),
	content: content
    };

    var infowindow = new google.maps.InfoWindow(options);
    map.setCenter(options.position);
}

function address(place) {
    var address = place;
    geocoder.geocode( { 'address': address}, function(results, status) {
	if (status == google.maps.GeocoderStatus.OK) {
	    map.setCenter(results[0].geometry.location);
	    var marker = new google.maps.Marker({
		map: map,
		position: results[0].geometry.location
	    });
	} 

	else {
	}

    });
}

function codeAddress() {
    var address = document.getElementById('address').value;
    geocoder.geocode( { 'address': address}, function(results, status) {
	if (status == google.maps.GeocoderStatus.OK) {
	    map.setCenter(results[0].geometry.location);
	    var marker = new google.maps.Marker({
		map: map,
		position: results[0].geometry.location
	    });
	} 
	else {
	}
    });
}

google.maps.event.addDomListener(window, 'load', initialize);
