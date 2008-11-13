// task.js

function memberFilter(account_id) {
  var sUrl = '?account=' + account_id;
  var callback = {
    success: function(o) {
      var members = document.getElementById('id_member');
      members.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);
}