//Focus cursor on input#login
function focusLogin() {
	$('input#id_username').focus();
}

//Detect and alert IE users to download firefox or chrome
function detectIE() {
	var message = '<div id="browser_message"><p>You are using Internet Explorer. MESS works best with a modern browser. Please download a free copy of <a href="http://www.mozilla.com/en-US/">Mozilla Firefox</a> or <a href="http://www.google.com/chrome">Google Chrome</a>.</p></div>';
	if ($.browser.msie) {
		window.setTimeout(function () {
			$(message).insertBefore('#container').hide().slideDown('fast');
		}, 500);
	}
}

//stuff automaticall run on pageload
$(document).ready(function() {	
	//hidd sub_nav on document.ready and display it when span.more is clicked
	$('.sub_nav').hide();
	$('#main_nav ul li .more').click(function() {
    $(this).toggleClass('open');
		$(this).parent().toggleClass('clicked');
    $(this).parent().next('.sub_nav').slideToggle(200);
	 });
	 $('body').click(function() {
	   $('.sub_nav').hide();
	 });
	
});