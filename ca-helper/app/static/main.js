$(function () {
  $('#init-ca').on('click', function (e) {
    e.preventDefault()
    $.getJSON('/init-ca',
      function (data) {
        //do nothing
      });
    return false;
  });
  // $('#create-cert').on('click', function (e) {
  //   e.preventDefault()
  //   $.post("/create-cert", $("#create-cert-form").serialize(), function (data) {
  //     // alert(data);
  //   });
  //   return false;
  // });
});