// create namespace object
YAHOO.namespace("schedule.calendar");

//define the initConnection
YAHOO.schedule.calendar.initConnection = function() {
    var div = YAHOO.util.Dom.get("task-list");

    function dateToLocaleString(dt) {
    	var dStr = dt.getDate();
    	var mStr = dt.getMonth()+1;
    	var yStr = dt.getFullYear();
    	return ("/scheduling/task_list/" + yStr + "-" + mStr + "-" + dStr);
    }

    var handleSuccess = function(response){
        if(response.responseText !== undefined){ 		    
            div.innerHTML = response.responseText;
        }
    };

    var handleFailure = function(response){ 
        if(response.responseText !== undefined){ 
            div.innerHTML = "Nothing for this Date"; 
        } 
    };
    
    var callback = 
	{ 
	    success: handleSuccess, 
	    failure: handleFailure,   
	};

    function mySelectHandler(type, args, obj) {
    	var selected = args[0];
    	var selDate = this.toDate(selected[0]);
    	var sUrl = dateToLocaleString(selDate);
    	getForm(null, selDate);
    	YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
    }
    
    YAHOO.schedule.calendar.cal1 = new YAHOO.widget.Calendar("cal1","cal1Container");
    YAHOO.schedule.calendar.cal1.selectEvent.subscribe(mySelectHandler, YAHOO.schedule.calendar.cal1, true);
    YAHOO.schedule.calendar.cal1.render();
    
    // list todays tasks on page load
    var sUrl = dateToLocaleString(new Date());
    YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
}

YAHOO.util.Event.onDOMReady(YAHOO.schedule.calendar.initConnection);

// create namespace object
YAHOO.namespace("schedule.tasks");

var handleSuccess = function(response){
    var heading_div = YAHOO.util.Dom.get("right-column-heading");
    var form_div = YAHOO.util.Dom.get("task-form");
    form_div.innerHTML = response.responseText;
    heading_div.innerHTML = response.argument[0];
    if (response.argument[1] !== undefined){
        var deadline = YAHOO.util.Dom.get("id_deadline");
        deadline.value = response.argument[1];
    }
};

var handleFailure = function(response){ 
    form_div.innerHTML = "Nothing for this Date";
};

function getForm(task_id, date) {
    if(task_id == null){
        arg = 'Create new task: ' + date;
        sUrl = '/scheduling/task_form/';
    } else {
        arg = 'Edit this task';
        sUrl = '/scheduling/task_form/' + task_id;
    }
    var callback = { 
        success: handleSuccess, 
        failure: handleFailure,
        argument: [arg, date]   
    };
    YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null); 
}

// Load New Task Form on Page Load
date =
getForm(null, date);