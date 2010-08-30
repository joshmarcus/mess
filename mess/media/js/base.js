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

function subNav() {
	
	var sub_nav = $('.sub_nav');
	
	$('#main_nav ul li .more').click(function() { //When trigger is clicked...
		
		//Following events are applied to the sub_nav itself (moving sub_nav up and down)
		$(this).parent().next(sub_nav).slideDown('fast'); //Drop down the sub_nav on click
		
		$(this).closest('li').hover(function() {
		}, function() {
			$(this).parent().find('.sub_nav').slideUp('slow'); //When the mouse hovers out of the containing li, move it back up
		});

	});
}

//stuff to automatically run on pageload
$(document).ready(function() {	
	subNav();
});