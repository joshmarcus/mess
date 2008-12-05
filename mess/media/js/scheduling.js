// create namespace object
YAHOO.namespace("schedule.calendar");

function dateToLocaleString(dt) {
	var dStr = dt.getDate();
	var mStr = dt.getMonth()+1;
	var yStr = dt.getFullYear();
	return (yStr + "-" + mStr + "-" + dStr);
}
	
function taskUrl(dt) {
    locale = dateToLocaleString(dt);
	return ("/scheduling/schedule/" + locale);
}

// define the initConnection
YAHOO.schedule.calendar.initConnection = function() {

    function mySelectHandler(type, args, obj) {
    	var selected = args[0];
    	var selDate = this.toDate(selected[0]);
    	var sUrl = taskUrl(selDate);
        window.location = sUrl;
    }
    
    YAHOO.schedule.calendar.cal1 = new YAHOO.widget.Calendar("cal1","cal1Container");
    YAHOO.schedule.calendar.cal1.selectEvent.subscribe(mySelectHandler, YAHOO.schedule.calendar.cal1, true);
    YAHOO.schedule.calendar.cal1.render();
    
    // list todays tasks on page load
    var sUrl = taskUrl(new Date());
}

YAHOO.util.Event.onDOMReady(YAHOO.schedule.calendar.initConnection);
