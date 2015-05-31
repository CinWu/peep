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

    $("#createE").on('click', function() {
	var event = $("#event").val();
	var date = $("#date").val();
	var time = $("#time").val();
	var description = $("#des").val();
	var tags = $("#tags").val();
	var loc = $("#address").val();

	if (event == "" || date=="" || time=="" || des=="" || loc==""){
	    alert("must fill out fields")
	}

	else {
	    var data = $('#createEvent').serialize();
	    data += "&location="+loc+"&submit=Create Event";
	    console.log(data);

	    $.ajax({
		url: "/create",
		data: data,
		type: "POST",
		success: function(response) {
		window.location.href = "/events"
		    console.log('success');
		    
		},
		error: function(error) {
                    console.log(error);
		}
            }); 
	}
    });
    map = new google.maps.Map(document.getElementById('map-canvas'), {
	mapTypeId: google.maps.MapTypeId.ROADMAP
    });	
});

var geocoder = new google.maps.Geocoder();
var map;

//Map
function initialize() {
    var markers = [];

    map = new google.maps.Map(document.getElementById('map-canvas'), {
	mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var done = $.Deferred();

    var pos = new google.maps.LatLng(0,0);
    if(navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(function(position) {
	    pos = new google.maps.LatLng(position.coords.latitude,
					     position.coords.longitude);
	    done.resolve();
	});}

    var defaultBounds = new google.maps.LatLngBounds(
	new google.maps.LatLng(50, -100),
	new google.maps.LatLng(-50, 100) 
    );
    map.fitBounds(defaultBounds);

    $.when(done).done(function() {
	console.log(pos);
	var userBounds = new google.maps.LatLngBounds(
	    new google.maps.LatLng(pos['A']+.0025, pos['F']-.0025),
	    new google.maps.LatLng(pos['A']-.0025, pos['F']+.0025) 
	);	
	map.fitBounds(userBounds);
    });

    var input = (
	document.getElementById('address'));
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    var searchBox = new google.maps.places.SearchBox((input));

    google.maps.event.addListener(searchBox, 'places_changed', function() {
	var places = searchBox.getPlaces();

	if (places.length == 0) {
	    return;
	}
	for (var i = 0, marker; marker = markers[i]; i++) {
	    marker.setMap(null);
	}

	markers = [];
	var bounds = new google.maps.LatLngBounds();
	for (var i = 0, place; place = places[i]; i++) {
	    var image = {
		url: place.icon,
		size: new google.maps.Size(71, 71),
		origin: new google.maps.Point(0, 0),
		anchor: new google.maps.Point(17, 34),
		scaledSize: new google.maps.Size(25, 25)
	    };

	    // Create a marker for each place.
	    var marker = new google.maps.Marker({
		map: map,
		title: place.name,
		position: place.geometry.location,
		animation: google.maps.Animation.DROP
	    });

	    markers.push(marker);
	    bounds.extend(place.geometry.location);
	}
	map.fitBounds(bounds);
    });

    // Bias the SearchBox results towards places that are within the bounds of the current map's viewport.
    google.maps.event.addListener(map, 'bounds_changed', function() {
	var bounds = map.getBounds();
	searchBox.setBounds(bounds);
    });
}

/*function initialize() {
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
}*/

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

//Center map at place
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

//Center map at user's location
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


//Finding Distance
var d = $.Deferred();

function locate(add, res) {
    var address = add;
    var loc=[];

    geocoder.geocode( { 'address': address }, function(results, status) {
	if (status == google.maps.GeocoderStatus.OK) {
            loc[0]=results[0].geometry.location.lat();
            loc[1]=results[0].geometry.location.lng();
	    console.log(loc);
//            alert( loc );
	} else {
            alert("Geocode was not successful for the following reason: " + status);
	}

	if (res) {
	    d.resolve();
	}	
    });


    return loc;
}

//Haversine formula
var rad = function(x) {
    return x * Math.PI / 180;
};

var distance = function(p1, p2) {
    var R = 6378137;
    var latlong1 = locate(p1, false);
    var latlong2 = locate(p2, true);
    
    $.when(d).done( function() {
	var dLat = rad(latlong1[0] - latlong2[0]);
	var dLong = rad(latlong1[1] - latlong2[1]);
	var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
	    Math.cos(rad(latlong1[0])) * Math.cos(rad(latlong2[0])) *
	    Math.sin(dLong / 2) * Math.sin(dLong / 2);
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
	var d = R * c;
	d = d*0.000621371;//meters to miles
	console.log(d);
	$.ajax({
	    url: "/",
            data: d,
	    type: "POST"
        });
    });
};
    

google.maps.event.addDomListener(window, 'load', initialize);
