$(function() {
  $('#reset-password-form').submit(function() {
    var form
    if (confirm('Click OK to send a password reset email to this user.')) {
      form = $(this)
      $.post(form.attr('action'), form.serialize(), function(data) {
        form.find(':submit').val('Email sent!').attr('disabled', true)
      })
    }
    return false
  })
})
