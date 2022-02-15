$(function() {
    var win1
    $(".kaipoke").on('click',function(){
        var url= "https://r.kaipoke.biz/kaipokebiz/login/COM020102.do"
        win1 = window.open(url, "kaipoke", "width=900,height=1000,scrollbars=yes");
    });
});