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
