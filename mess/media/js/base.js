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