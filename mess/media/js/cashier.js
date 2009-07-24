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

// fills in the form fields so you can reverse a previous transaction
function reverseit(transid, accountid, accountname, purchase_type, purchase_amount, payment_type, payment_amount) {
    document.getElementById('id_hidden_account').value = accountid;
    document.getElementById('id_account').value = accountname;
    document.getElementById('id_purchase_type').value = purchase_type;
    document.getElementById('id_purchase_amount').value = -purchase_amount;
    document.getElementById('id_payment_type').value = payment_type;
    document.getElementById('id_payment_amount').value = -payment_amount;
    document.getElementById('id_note').value = '@'+transid+' reversed because';
}

window.onload = function() {
  document.getElementById('id_account').focus();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
