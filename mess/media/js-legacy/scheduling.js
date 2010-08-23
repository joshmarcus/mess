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
  var sUrl = baseURL + '?index=' + totalForms.value + '&prefix=' + 
      formsetPrefix;
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
      var removeFormA = document.getElementById('remove-' + o.argument[0]);
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
    var removeFormA = document.getElementById('remove-' + formsetPrefix);
    YAHOO.util.Dom.addClass(removeFormA, 'hidden');
  }
  document.getElementById('save').focus();
}
function checkWorkers() {
  var totalForms = YAHOO.util.Selector.query('form input[id$="TOTAL_FORMS"]');
  for (i=0; i<totalForms.length; i++) {
    var totalForm = totalForms[i];
    if (totalForm.value > 1) {
      formPrefix = totalForm.name.replace('-TOTAL_FORMS', '');
      var removeFormA = document.getElementById('remove-' + formPrefix);
      YAHOO.util.Dom.removeClass(removeFormA, 'hidden');
    }
  }
}
function resetTaskDisplay() {
  var taskDisplays = YAHOO.util.Dom.getElementsByClassName('task-display', 'tr');
  var taskEdits = YAHOO.util.Dom.getElementsByClassName('task-edit', 'tr');
  YAHOO.util.Dom.addClass('task-add', 'hidden');
  YAHOO.util.Dom.removeClass(taskDisplays, 'hidden');
  YAHOO.util.Dom.addClass(taskEdits, 'hidden');
}
function taskAdd() {
  resetTaskDisplay();
  YAHOO.util.Dom.removeClass('task-add', 'hidden');
  document.forms.add.elements[1].select();
}
function taskAddCancel() {
  YAHOO.util.Dom.addClass('task-add', 'hidden');
}
function taskEditCancel(cancelButton) {
  var taskEdit = cancelButton.parentNode.parentNode.parentNode.parentNode.parentNode;
  var taskDisplay = YAHOO.util.Dom.getPreviousSibling(taskEdit);
  YAHOO.util.Dom.addClass(taskEdit, 'hidden');
  YAHOO.util.Dom.removeClass(taskDisplay, 'hidden');
}
function taskClick(e, taskDisplay) {
  resetTaskDisplay();
  var taskEdit = YAHOO.util.Dom.getNextSibling(taskDisplay);
  YAHOO.util.Dom.addClass(taskDisplay, 'hidden');
  YAHOO.util.Dom.removeClass(taskEdit, 'hidden');
  taskEdit.getElementsByTagName('form')[0].elements[2].select();
}
function hasClassClickable(node) {
  return YAHOO.util.Dom.hasClass(node, 'clickable');
}
function taskClickAssign() {
  var taskDisplays = YAHOO.util.Dom.getElementsByClassName('task-display', 'tr');
  for (i=0; i<taskDisplays.length; i++) {
    var taskDisplay = taskDisplays[i];
    var taskClickables = YAHOO.util.Dom.getChildrenBy(taskDisplay,hasClassClickable);
    for (j=0; j<taskClickables.length; j++) {
      YAHOO.util.Event.on(taskClickables[j], 'click', taskClick, taskDisplay);
    }
  }
}
function affectDisable(e) {
  var inputElement = YAHOO.util.Event.getTarget(e);
  var this_form = inputElement.form;
}
function timeBlurAssign() {
  var timeInputs = YAHOO.util.Selector.query('form input[id$="time_0"]');
  //YAHOO.util.Event.on(timeInputs, 'blur', timeBlur);
}

/*
function taskOptions(clickA) {
  var clickDiv = clickA.parentNode;
  var optionDiv = YAHOO.util.Dom.getNextSibling(clickDiv);
  if (YAHOO.util.Dom.hasClass(clickA, 'task-options-arrow')) {
    clickA.innerHTML = clickA.text.replace('↓', '←');
    YAHOO.util.Dom.removeClass(clickA, 'task-options-arrow');
    YAHOO.util.Dom.addClass(optionDiv, 'hidden');
  } else {
    clickA.innerHTML = clickA.text.replace('←', '↓');
    YAHOO.util.Dom.addClass(clickA, 'task-options-arrow');
    YAHOO.util.Dom.removeClass(optionDiv, 'hidden');
    YAHOO.util.Dom.addClass(optionDiv, 'task-options');
  }
  return false;
}
*/
