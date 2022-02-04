$(function() {

    $(".tag").on('click',function(){
        var scroll = new SmoothScroll('a[href*="."]');
        var headerH = 60; //ヘッダーの高さ
        tag_name = $(this).attr('class');
        tag_name = tag_name.split('tag scroll_')
        var target = $('.' + tag_name[1]).eq(0);
        var position = target.offset().top;
        var sc_pos = position - headerH;
        scrollTo(0,sc_pos);
    });

    $(document).on("click","#add_sche_btn",function(){
        //month_type
        var month_type = $('input[name=monthtype]:checked').val();
        if(month_type !="this" & month_type != "next"){
            alert("月の選択を確認してください。");
            return false;
        }
        //new_url
        var href = $(this).parent('a').attr('href');
        href = href.slice(0,-1);
        if(month_type == "next"){
            href = href + "_next";
        }
        //start_day end_day
        var start_day = Number($('#start_day').val())
        var end_day   = Number($('#end_day').val())

        if(start_day<1 |  start_day>31 | end_day<1 | end_day>31 | start_day>end_day){
            alert("日付の入力を確認してください。");
            return false;
        }
        //チェックのlist
        var def_sche_arr = [];
        $('input[name=add_sche_check]:checked').each(function(){
            // チェックされているの値を配列に格納
            def_sche_arr.push($(this).val());
        });
        if(def_sche_arr.length==0){
            alert("固定スケジュールが選択されていません。");
            return false;
        }
        params="?def_sche=" + def_sche_arr + "&start_day=" + start_day + "&end_day=" + end_day;
        //url
        href= href + params
        href = $(this).parent('a').attr('href',href);
        
        if(window.confirm("本当に追加してもよろしいですか？")){
            return true;
        }else{
            return false;
        }
    });

    
});