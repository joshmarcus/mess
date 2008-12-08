// for adding new forms to a formset
// TODO: generalize for forms not in tables
function addNew(formsetPrefix, baseURL) {
  var totalForms = document.getElementById('id_' + formsetPrefix + 
      '-TOTAL_FORMS');
  var sUrl = baseURL + '?index=' + totalForms.value;
  totalForms.value = parseInt(totalForms.value) + 1;
  var callback = {
    success: function(o) {
      var newFieldsTable = document.createElement('table');
      newFieldsTable.innerHTML = o.responseText;
      var newFields = document.createElement('div');
      newFields.className = 'added';
      newFields.appendChild(newFieldsTable);
      var writeRoot = document.getElementById(o.argument[0] + '-writeroot');
      writeRoot.parentNode.insertBefore(newFields, writeRoot);
      newFields = writeRoot.previousSibling;
      newFields.getElementsByTagName('select')[0].focus();
    },
    failure: function(o) {},
    argument: [formsetPrefix],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
}


