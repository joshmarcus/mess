{% for order in account.ebtbulkorder_set.unpaid %}

var pay = confirm('Would you like to pay for your EBT bulk order for ${{ order.amount }}?  OK=Yes, Cancel=No.');
if (pay) {
  if (document.getElementById('id_ebtbulkamount').value == 'None') {
    document.getElementById('id_ebtbulkamount').value = {{ order.amount }};
    document.getElementById('id_ebtbulkorders').value = {{ order.id }};
  } else {
    document.getElementById('id_ebtbulkamount').value = 
        (document.getElementById('id_ebtbulkamount').value - 
         (-{{ order.amount }})).toFixed(2);
    document.getElementById('id_ebtbulkorders').value += ',' + {{ order.id }};
  }
  ebtautocalc();
}

{% endfor %}
