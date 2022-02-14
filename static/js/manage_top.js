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

    $("#show_allerrors").change(function(){
      if($('#show_allerrors').prop('checked')==true){
          $("#search_form").append("<input type='hidden' name='show_allerrors' value='true'>");
          $("#search_form").submit();
      }else{
        $("#search_form").submit();
      }  
    });
    
    $(document).on("click",".btn-danger",function(){
        if(window.confirm("実行してもよろしいですか？")){
          return true;
        }else{
          return false;
        }
    });
});