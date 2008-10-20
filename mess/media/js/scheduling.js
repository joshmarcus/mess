// create namespace object
YAHOO.namespace("schedule.calendar");

// date formatting

var month=new Array(12);
month[0]="January";
month[1]="February";
month[2]="March";
month[3]="April";
month[4]="May";
month[5]="June";
month[6]="July";
month[7]="August";
month[8]="September";
month[9]="October";
month[10]="November";
month[11]="December";

function formatDateForHeading(dt) {
	var dStr = dt.getDate();
	var mStr = month[dt.getMonth()];
	var yStr = dt.getFullYear();
	return (mStr + " " + dStr + ", " + yStr);
}

function formatDateForDeadline(dt) {
	var dStr = dt.getDate();
	var mStr = dt.getMonth()+1;
	var yStr = dt.getFullYear();
	return (yStr + "-" + mStr + "-" + dStr);
}

function dateToLocaleString(dt) {
	var dStr = dt.getDate();
	var mStr = dt.getMonth()+1;
	var yStr = dt.getFullYear();
	return (yStr + "-" + mStr + "-" + dStr);
}
	
function taskUrl(dt) {
    locale = dateToLocaleString(dt);
	return ("/scheduling/task_list/" + locale);
}

// define the initConnection
YAHOO.schedule.calendar.initConnection = function() {
    var div = YAHOO.util.Dom.get("task-list");

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
    	var sUrl = taskUrl(selDate);
    	getForm(null, selDate);
    	YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
    }
    
    YAHOO.schedule.calendar.cal1 = new YAHOO.widget.Calendar("cal1","cal1Container");
    YAHOO.schedule.calendar.cal1.selectEvent.subscribe(mySelectHandler, YAHOO.schedule.calendar.cal1, true);
    YAHOO.schedule.calendar.cal1.render();
    
    // list todays tasks on page load
    var sUrl = taskUrl(new Date());
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

function getForm(task_id, dt) {
    if(task_id == null){
        date = formatDateForHeading(dt);
        header = 'Create new task: ' + date;
        sUrl = '/scheduling/task_form/';
        date = formatDateForDeadline(dt);
    } else {
        header = 'Edit this task:';
        sUrl = '/scheduling/task_form/' + task_id;
    }
    var callback = { 
        success: handleSuccess, 
        failure: handleFailure,
        argument: [header, date]   
    };
    YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null); 
}

function deleteTask(task_id) {
    if (confirm("Are you sure you want to remove this task?")){
        var handleSuccess = function(response){
            // var task_id_div = YAHOO.util.Dom.get('task'+task_id);
            // task_id_div.innerHTML = response.argument[0];
            // YAHOO.util.Dom.replaceClass(task_id_div, 'hidden');          
        };
        var callback = { 
            success: handleSuccess
        };
        sUrl='/scheduling/task/delete/' + task_id;
        YAHOO.util.Connect.asyncRequest('POST', sUrl, callback, null);
        // location ='/scheduling/task/delete/' + task_id;
    }
}

// Load New Task Form on Page Load
var today = new Date();
getForm(null, today);