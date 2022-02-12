const timer = 7200000 // 2時間毎にリロード
window.addEventListener('load',function(){
  setInterval('location.reload()',timer);
});
$(function() {
    //hover時のポップ表示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    $('#search_form').submit(function() {
        var staff = $('#staff').val();
        if (staff === undefined || staff === "") {
          $('#staff').attr('name','empty_staff');
        } else {
          $('#staff').attr('name','staff');
        }
    });

    $("#staff").change(function(){
        $("#search_form").submit();
    });
    $(".month_btn").on('click',function(){
        var send_url = $(this).parents('a').attr('href');
        url_arr = send_url.split('?');
        send_url = url_arr[0];
        var add_param = "";
        var staff = $('#staff').val();
        if (staff !== undefined && staff !== ""){
          if(add_param ==""){
            add_param += "?";
          }
          add_param += "staff=" + staff;
        }
        send_url = send_url + add_param;
        $(this).parents('a').attr('href',send_url);
    });
    $("#reload_btn").on('click',function(){
        location.reload();
    });
});