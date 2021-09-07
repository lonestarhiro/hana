$(function() {

    function change_year_text(year_select_obj){

        var cnt = year_select_obj.length;
        for(var i=1;i<=cnt;i++){
            var year = year_select_obj.eq(i).val();
            year = year-0;
            var nengou;
            var jp_year;
            if(year<1912){
                nengou="明治";
                jp_year=nengou + (year-1867) + "年/" + year + "年";
            }else if(year<1926){
                nengou="大正";
                jp_year=nengou + (year-1911) + "年/" + year + "年";
            }else if(year<1989){
                nengou="昭和";
                jp_year=nengou + (year-1925) + "年/" + year + "年";
            }else if(year<2019){
                nengou="平成";
                jp_year=nengou + (year-1988) + "年/" + year + "年";
            }else{
                nengou="令和";
                jp_year=nengou + (year-2018) + "年/" + year + "年";
            }
            //alert(jp_year)
            year_select_obj.eq(i).text(jp_year);
        }
        return false;
    }
    
    function change_day_text(day_select_obj){
        cnt = day_select_obj.length;
        for(var i=1;i<=cnt;i++){
            var new_text = day_select_obj.eq(i).text() + "日";
            day_select_obj.eq(i).text(new_text)
        }
    }
    var obj = $("#div_id_birthday").children("#id_birthday_year").find('option');
    change_year_text(obj);

    obj = $("#div_id_birthday").children("#id_birthday_day").find('option');
    change_day_text(obj);

    obj = $("#div_id_join").children("#id_join_year").find('option');
    change_year_text(obj);

    obj = $("#div_id_join").children("#id_join_day").find('option');
    change_day_text(obj);
});