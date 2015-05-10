$(document).ready( function() {
   
    $('#search').click(function() {
	var peep = ($('#peep').val());
	var at = ($('#at').val());
	if ( peep == "" && at == "" ) {
	    window.location.href = "/events";
	}
    });
    
    $('#create').click(function() {
	window.location.href = "/create";
    });

});
