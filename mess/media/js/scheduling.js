// create namespace object
YAHOO.namespace("schedule");

function LZ(n) {
  return (n > 9 ? n : '0' + n);
}
function formatDate(dateObj, ISO) {
  if (ISO == 1)
    return dateObj.getFullYear() + '-' + LZ((dateObj.getMonth()+1)) + '-' + LZ(dateObj.getDate());
  return LZ((dateObj.getMonth()+1)) + '/' + LZ(dateObj.getDate()) + '/' + dateObj.getFullYear();
}
function taskUrl(dateObj) {
	return ("/scheduling/schedule/" + formatDate(dateObj, 1));
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
      cell.innerHTML = '<a href="' + taskUrl(cellDate) + '">' + cellDate.getDate() + "</a><br>" + days[formatDate(cellDate)];
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
      var removeFormA = document.getElementById(o.argument[0] + '-remove');
      YAHOO.util.Dom.removeClass(removeFormA, 'hidden');
    },
    failure: function(o) {},
    argument: [formsetPrefix],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
}
// and removing
function removeForm(formsetPrefix) {
  var totalForms = document.getElementById('id_' + formsetPrefix + 
      '-TOTAL_FORMS');
  totalForms.value = parseInt(totalForms.value) - 1;
  var writeRoot = document.getElementById(formsetPrefix + '-writeroot');
  lastForm = YAHOO.util.Dom.getPreviousSibling(writeRoot);
  lastForm.parentNode.removeChild(lastForm);
  if (totalForms.value == 1) {
    var removeFormA = document.getElementById(formsetPrefix + '-remove');
    YAHOO.util.Dom.addClass(removeFormA, 'hidden');
  }
  document.getElementById('save').focus();
}

function checkWorker() {
  var totalForms = document.getElementById('id_worker-TOTAL_FORMS');
  if (totalForms.value > 1) {
    var removeFormA = document.getElementById('worker-remove');
    YAHOO.util.Dom.removeClass(removeFormA, 'hidden');
  }
}
function taskAdd() {
  YAHOO.util.Dom.removeClass('task-add', 'hidden');
  document.forms.add.time_1.select();
}

