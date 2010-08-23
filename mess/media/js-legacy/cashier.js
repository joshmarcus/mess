// cashier.js

function getAccountInfo(account_id) {
// FIXME this new code needs some clean up

  if (typeof(window['EBTBULKORDERS']) == 'undefined') {
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
  }

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

  if (typeof(window['EBTBULKORDERS']) != 'undefined' && EBTBULKORDERS) {
    sUrl = '?getcashierinfo=ebtbulkorders&account=' + account_id;
    ebtbulkorders_callback = {
        success: function(o) {
            //alert('okay, this alert should work.');
            //eval('alert(8777);');
            eval(o.responseText);
        },
        failure: function(o) {},
        argument: [],
    };
    YAHOO.util.Connect.asyncRequest('GET', sUrl, ebtbulkorders_callback, null);
  }
}

// prompts you to reverse a previous transaction
function reverse_trans(trans_id) {
    reason = prompt('Please explain why you are reversing this transaction.  (Transactions should only be reversed when absolutely necessary, as it complicates accounting.)');
    if (reason == undefined) return;
    document.getElementById('id_reverse_id').value = trans_id;
    document.getElementById('id_reverse_reason').value = reason;
    document.getElementById('reverse_form').submit();
}

function ebtautocalc() {
  var charge = document.getElementById('id_regular_sales').value;
  if (document.getElementById('id_ebtbulkamount').value != 'None') {
    charge -= -document.getElementById('id_ebtbulkamount').value;
  }
  document.getElementById('ebttotalamount').value = (-(-charge)).toFixed(2);
}

window.onload = function() {
  document.getElementById('id_account').focus();
  if (typeof(window['EBTBULKORDERS']) != 'undefined' && EBTBULKORDERS) {
    document.getElementById('id_regular_sales').onchange = ebtautocalc;
  }
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
