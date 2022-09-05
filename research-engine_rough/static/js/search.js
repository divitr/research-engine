$(function(){
	$('button').click(function(){
		var user = $('#inputUsername').val();
		var pass = $('#inputPassword').val();
		$.ajax({
			url: '/signUpUser',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

function initiateAllAjax() {
	$('a[class="search-url"]').each(function(i,obj){
		//alert($(obj).attr('href'));
		initiateAjax(obj);
	});
}

function initiateAjax(aobj) {
	var url = $(aobj).attr('href');
	var parent = $(aobj).parent( ".search-result" );
	var targetElement = $(parent).children(".summary-loaded")
	var loadingElements = $(parent).children(".summary-loading")
	$(loadingElements).show(100);
	$(targetElement).fadeOut();

	$.ajax({
		url: '/summarize',
		data: url,
		type: 'POST',
		success: function(response){
			//alert("response" + response + " for " + structuredClone(url))
			//alert(($(parent)).html);
			$(targetElement).show(100);
			$(targetElement).html(response);
			$(loadingElements).slideUp();
		},
		error: function(error){
			//console.log(error);
			//alert("error" + error)
			$(targetElement).show(100);
			$(targetElement).html("ERROR: " + error);
			$(loadingElements).slideUp();
		}
	});
};
