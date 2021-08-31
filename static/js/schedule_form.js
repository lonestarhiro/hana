$(function() {
    var peaples_select = $('#id_peoples').val();
    var cnt=1;
    //担当スタッフ欄の表示
    while(cnt<=4){
        if(cnt <= peaples_select){
            $('#div_id_staff'+ cnt).show();
        }else{
            $('#div_id_staff'+ cnt).hide();
            $('#id_staff'+ cnt).val("");
        }
        cnt++;
    }
    //研修スタッフ欄の表示
    cnt=4
    while(cnt>0){
        var tr_staff = $('#id_tr_staff'+ (cnt-1)).val();

        if(tr_staff ==""){
            $('#div_id_tr_staff'+ cnt).hide();
            $('#tr_staff'+ cnt).val("");
        }
        cnt--;  
    }

    //担当スタッフ欄の表示
    $('#id_peoples').change(function() {
        peaples_select = $('#id_peoples option:selected').val();

        cnt=1;
        while(cnt<=4){
            if(cnt <= peaples_select){
                $('#div_id_staff'+ cnt).show();
            }else{
                $('#div_id_staff'+ cnt).hide();
                $('#id_staff'+ cnt).val("");
            }
            cnt++;
        }
    })
    //研修スタッフ欄の表示
    $("[id^=id_tr_staff]").change(function() {

        //現在の値をすべて取得
        cnt=1
        var tr_staff_val=[];
        while(cnt<=4){
            if($('#id_tr_staff'+ cnt).val() !=""){
                if($.inArray($('#id_tr_staff'+ cnt).val(),tr_staff_val)==-1){
                    tr_staff_val.push($('#id_tr_staff'+ cnt).val());
                }
            }
            cnt++;  
        }
        
        //値をセットし直す
        cnt=4
        while(cnt>=1){
            if(cnt > tr_staff_val.length+1){
                $('#id_tr_staff' + cnt).val("");
                $('#div_id_tr_staff' + cnt).hide();

            }else if(cnt == tr_staff_val.length+1){
                $('#id_tr_staff' + cnt).val("");
                $('#div_id_tr_staff' + cnt).show();
            }else{
                $('#id_tr_staff' + cnt).val(tr_staff_val[cnt-1]);
                $('#div_id_tr_staff' + cnt).show();
            }
            cnt--;  
        }
    })
});