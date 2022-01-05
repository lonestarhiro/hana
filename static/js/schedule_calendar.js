$(function() {

    //全体一覧表示時アンカーへスクロール
    if ($("#anchor").length>0){
        var scroll = new SmoothScroll('a[href*="#"]');
        var headerH = 225; //ヘッダーの高さ
        var target = $("#anchor").eq(0);
        var position = target.offset().top;
        var sc_pos = position - headerH;
        scrollTo(0,sc_pos);
        //document.getElementById('anchor').scrollIntoView({behavior: "smooth"});
    }

    $('#search_form').submit(function() {
        var staff = $('#staff').val();
        var careuser = $('#careuser').val();
        if (staff === undefined || staff === "") {
          $('#staff').attr('name','empty_staff');
        } else {
          $('#staff').attr('name','staff');
        }
        if (careuser === undefined || careuser === "") {
          $('#careuser').attr('name','empty_careuser');
        } else {
          $('#careuser').attr('name','careuser');
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

    $(".print_btn,.month_btn").on('click',function(){
        var send_url = $(this).parents('a').attr('href');
        url_arr = send_url.split('?');
        send_url = url_arr[0];
        var add_param = "";
        var staff = $('#staff').val();
        var careuser = $('#careuser').val();
        if (staff !== undefined && staff !== ""){
          if(add_param ==""){
            add_param += "?";
          }
          add_param += "staff=" + staff;
        }else if (careuser !== undefined && careuser !== ""){
          if(add_param ==""){
            add_param += "?";
          }
          add_param += "careuser=" + careuser;
        }
        send_url = send_url + add_param;
        $(this).parents('a').attr('href',send_url);
    });
    $(".td_day").on('click',function(){
        var send_url = $(this).attr('href');
        url_arr = send_url.split('?');
        send_url = url_arr[0];
        var add_param = "";
        var staff = $('#staff').val();
        var careuser = $('#careuser').val();
        if (staff !== undefined && staff !== ""){
          if(add_param ==""){
            add_param += "?";
          }
          add_param += "staff=" + staff;
        }else if (careuser !== undefined && careuser !== ""){
          if(add_param ==""){
            add_param += "?";
          }
          add_param += "careuser=" + careuser;
        }
        send_url = send_url + add_param;
        window.location.href = send_url;
    });
});