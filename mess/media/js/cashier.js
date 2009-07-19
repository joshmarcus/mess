// cashier.js

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

window.onload = function() {
  document.getElementById('id_account').focus();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;

/*
function getTransactions(id) {
  var query = "?search=transactions"
  if (id == parseInt(id)) {  
    query += "&account_id=" + document.getElementById('id_account').value
  }
  xhr(query,'transactions');
}
*/
