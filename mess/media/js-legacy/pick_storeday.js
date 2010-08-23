function pick_storeday(selectbox) {
  if (selectbox.value == '') { return; }
  startend = selectbox.value.split('~');
  document.getElementById('id_start').value = startend[0];
  document.getElementById('id_end').value = startend[1];
}
