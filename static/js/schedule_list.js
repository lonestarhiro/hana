$(function() {
    //hover時のポップ表示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    //他のページからの戻り時アンカーへスクロール
    if ($("#anchor").length>0){
      var scroll = new SmoothScroll('a[href*="#"]');
      var headerH = 305; //ヘッダーの高さ
      var target = $("#anchor").eq(0);
      var position = target.offset().top;
      var sc_pos = position - headerH;
      scrollTo(0,sc_pos);
      //$('html, body').animate({scrollTop:sc_pos},100,'swing');
      //document.getElementById('anchor').scrollIntoView({behavior: "smooth"});
    }

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
        var service_kind = $('#service_kind').val();
        if (service_kind === undefined || service_kind === "") {
          $('#service_kind').attr('kind','empty_kind');
        } else {
          $('#service_kind').attr('name','service_kind');
        }
    });
    $("#careuser,#staff,#service_kind").change(function(){
        $("#search_form").submit();
    });
    $(".month_btn").on('click',function(){
        var send_url = $(this).parents('a').attr('href');
        var add_param = "";
        var careuser = $('#careuser').val();
        if (careuser !== undefined && careuser !== ""){
            if(add_param ==""){
              add_param += "?";
            }
            add_param += "careuser=" + careuser;
        }
        var staff = $('#staff').val();
        if (staff !== undefined && staff !== ""){
          if(add_param ==""){
            add_param += "?";
          }else{
            add_param += "&";
          }
          add_param += "staff=" + staff;
        }
        var service_kind = $('#service_kind').val();
        if (service_kind !== undefined && service_kind !== ""){
          if(add_param ==""){
            add_param += "?";
          }else{
            add_param += "&";
          }
          add_param += "service_kind=" + service_kind;
        }
        send_url = send_url + add_param;
        $(this).parents('a').attr('href',send_url);
    });
});