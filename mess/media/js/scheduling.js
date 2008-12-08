// create namespace object
YAHOO.namespace("schedule");

function taskUrl(dt) {
	var tskDate = (dt.getFullYear() + "-" + (dt.getMonth()+1) + "-" + dt.getDate());
	return ("/scheduling/schedule/" + tskDate);
}

function LZ(n) {
return (n > 9 ? n : '0' + n);
}

// setup calendar
YAHOO.schedule.setupCal = function() {

    function mySelectHandler(type, args, obj) {
    	var selected = args[0];
    	var selDate = this.toDate(selected[0]);
    	var sUrl = taskUrl(selDate);
        window.location = sUrl;
    }

    myRender = function(cellDate, cell) {
        fmtDate = LZ((cellDate.getMonth()+1)) + '/' + LZ(cellDate.getDate()) + '/' + cellDate.getFullYear();
        fmtDate2 = cellDate.getFullYear() + '-' + LZ((cellDate.getMonth()+1)) + '-' + LZ(cellDate.getDate());
        cell.innerHTML = '<a href="/scheduling/schedule/'+ fmtDate2 +'/">' + cellDate.getDate() + "</a><br>" + days[fmtDate];
        return YAHOO.widget.Calendar.STOP_RENDER;   
    }
    
    YAHOO.schedule.cal1 = new YAHOO.widget.Calendar("cal1", "cal1Container");

    for (day in days) {
        YAHOO.schedule.cal1.addRenderer(day, myRender);
    }
    //YAHOO.schedule.cal1.selectEvent.subscribe(mySelectHandler, YAHOO.schedule.cal1, true);
    YAHOO.schedule.cal1.render();
}

YAHOO.util.Event.onDOMReady(YAHOO.schedule.setupCal);

// for adding a form to a formset
function addForm(formsetPrefix, baseURL) {
  var totalForms = document.getElementById('id_' + formsetPrefix + 
      '-TOTAL_FORMS');
  var sUrl = baseURL + '?index=' + totalForms.value;
  totalForms.value = parseInt(totalForms.value) + 1;
  var callback = {
    success: function(o) {
      var newFields = document.createElement('li');
      newFields.innerHTML = o.responseText;
      var writeRoot = document.getElementById(o.argument[0] + '-writeroot');
      writeRoot.parentNode.insertBefore(newFields, writeRoot);
      // focus on first element in added form
      newFields = writeRoot.previousSibling;
      newFields.getElementsByTagName('select')[0].focus();
    },
    failure: function(o) {},
    argument: [formsetPrefix],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
}


