//create the namespace object for this example 
YAHOO.namespace("yuibook.calendar");
//define the lauchCal function which creates the calendar 
YAHOO.yuibook.calendar.launchCal = function() {
    // create the calendar object, specifying the container
    Var myCal = new YAHOO.widget.Calendar("mycal");
    //draw the calendar on screen 
    myCal.render(); 
    //hide it again straight away 
    myCal.hide(); 
} 

//define the showCal function which shows the calendar 
Var showCal = function() { 

  //show the calendar 
  myCal.show(); 
}

//create calendar on page load 
YAHOO.util.Event.onDOMReady(YAHOO.yuibook.calendar.launchCal); 
Event.onDOMReady(YAHOO.yuibook.calendar.launchCal); 
.onDOMReady(YAHOO.yuibook.calendar.launchCal); 

//attach listener for click event on calendar icon 
YAHOO.util.Event.addListener("calico", "click", showCal); 

