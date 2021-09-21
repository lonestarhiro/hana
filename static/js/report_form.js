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

    //必要人数の変更時
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

    //担当スタッフ欄の変更時
    $("[id^=id_staff]").change(function() {

        var newstaff = $(this).val();
        //必要人数
        var needs = $('#id_peoples option:selected').val();

        //担当スタッフとの重複を除去///////////////////////////////////
        cnt=1
        var staff_val=[];
        while(cnt<=needs){
            //担当に登録中のスタッフを取得
            if($('#id_staff'+ cnt).val() != "" && $('#id_staff'+ cnt).val() !=undefined){
                if($.inArray($('#id_staff'+ cnt).val(),staff_val)==-1){
                    staff_val.push($('#id_staff'+ cnt).val());
                }
            }
            cnt++;  
        }

        //値をセットし直す
        cnt=1;
        while(cnt<=4){
            if(cnt <= needs){
                $('#div_id_staff'+ cnt).show();
                if(cnt<=staff_val.length){
                    $('#id_staff'+ cnt).val(staff_val[cnt-1]);
                }else{
                    $('#id_staff'+ cnt).val("");
                }          
            }else{
                $('#div_id_staff'+ cnt).hide();
                $('#id_staff'+ cnt).val("");
            }
            cnt++;
        }
   
        //研修スタッフとの重複を除去///////////////////////////////////
        cnt=1
        var tr_staff_val=[];
        while(cnt<=4){
            //新しく設定した担当スタッフや未選択でなければ取得
            if($('#id_tr_staff'+ cnt).val() !="" && $('#id_tr_staff'+ cnt).val() !=undefined && $('#id_tr_staff'+ cnt).val() != newstaff){
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


    //研修スタッフ欄の変更時
    $("[id^=id_tr_staff]").change(function() {

        var newstaff = $(this).val();
        
        //担当スタッフとの重複を除去///////////////////////////////////
        //必要人数
        var needs = $('#id_peoples option:selected').val();

        cnt=1
        var staff_val=[];

        while(cnt<=needs){
            //新しく設定した同行スタッフや未選択でなければ取得
            if( $('#id_staff'+ cnt).val() != "" && $('#id_staff'+ cnt).val() !=undefined && $('#id_staff'+ cnt).val() != newstaff){
                if($.inArray($('#id_staff'+ cnt).val(),staff_val)==-1){
                    staff_val.push($('#id_staff'+ cnt).val());
                }
            }
            cnt++;  
        }

        //値をセットし直す
        cnt=1;
        while(cnt<=4){
            if(cnt <= needs){
                $('#div_id_staff'+ cnt).show();
                if(cnt<=staff_val.length){
                    $('#id_staff'+ cnt).val(staff_val[cnt-1]);
                }else{
                    $('#id_staff'+ cnt).val("");
                }          
            }else{
                $('#div_id_staff'+ cnt).hide();
                $('#id_staff'+ cnt).val("");
            }
            cnt++;
        }
   
        //研修スタッフとの重複を除去///////////////////////////////////
        //現在の値をすべて取得
        cnt=1
        var tr_staff_val=[];
        while(cnt<=4){
            //未選択でなければ配列に記録
            if($('#id_tr_staff'+ cnt).val() !="" && $('#id_tr_staff'+ cnt).val() !=undefined){
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