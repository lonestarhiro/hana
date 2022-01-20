$(function() {
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
    $("#staff").change(function(){
      $('#careuser').val(undefined);
        $("#search_form").submit();
    });

    $("#careuser").change(function(){
      $('#staff').val(undefined);
        $("#search_form").submit();
    });
});