// cashier.js

function getAccountInfo(account_id) {
// FIXME this new code needs some clean up

  var sUrl = '?getcashierinfo=members&account=' + account_id;
  var callback = {
    success: function(o) {
      var members = document.getElementById('id_member');
      members.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

  sUrl = '?getcashierinfo=acctinfo&account=' + account_id;
  acctinfo_callback = {
    success: function(o) {
      var dest = document.getElementById('acctinfo');
      dest.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, acctinfo_callback, null);

  sUrl = '?getcashierinfo=transactions&account=' + account_id;
  transax_callback = {
    success: function(o) {
      var transax = document.getElementById('transactions');
      transax.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, transax_callback, null);

}

window.onload = function() {
  document.getElementById('id_account').focus();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
