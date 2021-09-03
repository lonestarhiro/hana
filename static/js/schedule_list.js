$(function() {
    //hover時のポップ表示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    $('#search_form').submit(function() {
      var careuser = $('#careuser').val();
      if (careuser === undefined || careuser === "") {
        $('#careuser').attr('name','empty_careuser');
      } else {
        $('#careuser').attr('name','careuser'); 
      }
      var staff = $('#staff').val();
      if (staff === undefined || staff === "") {
        $('#staff').attr('name','empty_staff');
      } else {
        $('#staff').attr('name','staff');
      }
    });

    $("#careuser,#staff").change(function(){
      $("#search_form").submit();
    });
    
});