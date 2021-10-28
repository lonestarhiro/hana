$(function() {

    $(".tag").on('click',function(){
        var headerH = 200; //ヘッダーの高さ
        tag_name = $(this).attr('class');
        tag_name = tag_name.split('tag scroll_')
        var target = $('.' + tag_name[1]).eq(0);
        var position = target.offset().top;
        $(window).scrollTop(position - headerH);
    });
    
});