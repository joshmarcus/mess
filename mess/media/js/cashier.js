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

// prompts you to reverse a previous transaction
function reverse_trans(trans_id) {
    reason = prompt('Please explain why you are reversing this transaction.  (Transactions should only be reversed when absolutely necessary, as it complicates accounting.)');
    if (reason == undefined) return;
    document.getElementById('id_reverse_id').value = trans_id;
    document.getElementById('id_reverse_reason').value = reason;
    document.getElementById('reverse_form').submit();
}

window.onload = function() {
  document.getElementById('id_account').focus();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
