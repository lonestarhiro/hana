$(function() {
  
    const fields_and_max={
        "body_temp":45,
        "blood_pre_h":300,
        "blood_pre_l":300,
        "urination_t":99,
        "urination_a":9999,
        "defecation_t":99,
        "eat_a":100,
        "drink_a":9999,
        "deposit":999999,
        "payment":999999,
    }
    const fields_and_length={
        "defecation_s":50,
        "jir_together":50,
        "cook_menu":50,
    }
    //onload
    onload_in_time_change();
    main_check();

    //逆順
    $('#mix_reverse_btn').on('click',function(){
        in_time_change();
    });

    //メイン##########################################################################
    var trigger_id = "";
    trigger_id  = "#id_service_in_date_0,#id_service_out_date_0,#id_service_in_date_1,#id_service_out_date_1,";
    trigger_id += "#id_in_time_main,#id_in_time_sub,#id_destination,#id_communicate,#id_biko,";
    trigger_id += "#id_body_temp,#id_blood_pre_h,#id_blood_pre_l,#id_urination_t,#id_urination_a,";
    trigger_id += "#id_defecation_t,#id_defecation_s,#id_jir_together,#id_cook_menu,#id_eat_a,#id_drink_a,#id_deposit,#id_payment"

    $(trigger_id).blur(function(){
        //押されたidを送る
        var inputed = $(this).attr("id");
        main_check(inputed);
    });
    //###############################################################################

    function main_check(inputed_id){
        //safari等では日時の‐を/に変換しないと計算できない。
        var start = new Date($('#id_service_in_date_0').val().replace(/-/g,"/")  + " " + $('#id_service_in_date_1').val().replace(/-/g,"/"));
        var end   = new Date($('#id_service_out_date_0').val().replace(/-/g,"/") + " " + $('#id_service_out_date_1').val().replace(/-/g,"/"));
        var min_time = Number($('#min_time').val());
        var def_time = Number($('#time').val());
        var ope_time = get_ope_time(start,end);
        var in_time_main = $('#id_in_time_main').val();
        var in_time_sub  = $('#id_in_time_sub').val();
        var msg;

        //初期化
        input_color_change("service_in_date_1,service_out_date_1,in_time_main,in_time_sub","text-body");
        delete_time_err();
        delete_in_time_err();
        //送信後のバリデーションによるエラーも消す。
        delete_validation_err("service_in_date,service_out_date,in_time_main,in_time_sub");
        remove_highlight("service_in_date_0,service_in_date_1,service_out_date_0,service_out_date_1,in_time_main,in_time_sub");
 
        //複合サービスの場合上書き
        if(min_time==0){
            min_time = Number($('#min_time_main').val()) + Number($('#min_time_sub').val());
        }
        if(start>=end){
            msg = "日時の入力を確認してください。";
            output_time_err(msg,"text-danger");
            highlight_input("service_in_date_1,service_out_date_1");
        }else{
            if(ope_time_is_err(ope_time,min_time)){
                msg = "予定サービスの必要時間に達していません。<br>この状態でも登録可能は可能です。<br>下記にサービス変更事由を記載願います。";
                output_time_err(msg,"text-primary");
                input_color_change("service_in_date_1,service_out_date_1","text-primary");
            }
            if(time_is_over(ope_time,def_time)){
                msg = "予定サービス時間を超過しています。<br>この状態でも登録可能は可能です。<br>下記にサービス変更事由を記載願います。";
                output_time_err(msg,"text-primary");
                input_color_change("service_in_date_1,service_out_date_1","text-primary");
            }
        }
        if(typeof in_time_main !== undefined){
            //内訳の片方が押された場合は、もう片方の値を変更する。
            if(inputed_id == "id_in_time_main"){
                var new_time = (ope_time-$("#"+inputed_id).val()>0) ? ope_time-$("#"+inputed_id).val():0;                
                $("#id_in_time_sub").val(new_time);
            }else if(inputed_id == "id_in_time_sub"){
                var new_time = (ope_time-$("#"+inputed_id).val()>0) ? ope_time-$("#"+inputed_id).val():0;
                $("#id_in_time_main").val(new_time);
            }

            var in_time_main  = Number($('#id_in_time_main').val());
            var in_time_sub   = Number($('#id_in_time_sub').val());
            var min_time_main = Number($('#min_time_main').val());
            var min_time_sub  = Number($('#min_time_sub').val());

            if(ope_time != (in_time_main + in_time_sub)){
                msg="内訳の時間配分を確認して下さい。";
                output_in_time_err(msg,"text-danger");
                highlight_input("in_time_main,in_time_sub");
            }else{
                if(ope_time_is_err(in_time_main,min_time_main)){
                    msg = "サービス内訳が必要最低時間未満です。<br>この状態でも登録可能は可能です。<br>下記にサービス変更事由を記載願います。";
                    output_in_time_err(msg,"text-primary");
                    input_color_change("in_time_main","text-primary");
                    //$("#modal_body").html("内訳のサービスの必要最低時間に達していません。")
                    //$(".modal").modal("show");
                    //$("#id_in_time_main").addClass('text-danger');
                }
                if(ope_time_is_err(in_time_sub,min_time_sub)){
                    msg = "サービス内訳が必要最低時間未満です。<br>この状態でも登録可能は可能です。<br>下記にサービス変更事由を記載願います。";
                    output_in_time_err(msg,"text-primary");
                    input_color_change("in_time_sub","text-primary");
                }
            }
        }
        sub_check(fields_and_max,fields_and_length);
        destination_check();
        communicate_check();
        biko_check();
        submit_check();
    }
    function sub_check(fields_and_max,fields_and_length){
        //intの最大値チェック
        for(const [key, value] of Object.entries(fields_and_max)){
            if($("#id_"+key).val() <= value | $("#id_"+key).val() <0){
                delete_validation_err(key);
                remove_highlight(key);
            }else{
                delete_validation_err(key);
                add_validation_err(key,"この値は " + value + " 以下でなければなりません。");
                highlight_input(key);
            }
        }
        //お釣り計算
        if($("#id_deposit").hasClass("is-invalid")==false && $("#id_payment").hasClass("is-invalid")==false){
            var otsuri = $("#id_deposit").val()-$("#id_payment").val();
            if(otsuri<0){
                otsuri = -(otsuri);
                $("#otsuri_title").addClass("text-danger");
                $("#otsuri_title").text("請求額")
            }else{
                $("#otsuri_title").removeClass("text-danger");
                $("#otsuri_title").text("お釣り")
            }
            $("#otsuri").text(otsuri.toLocaleString() + " 円");
        }
        //length最大値チェック
        for(const [key, value] of Object.entries(fields_and_length)){
            if($("#id_"+key).val().length <= value | $("#id_"+key).val().length <0){
                delete_validation_err(key);
                remove_highlight(key);
            }else{
                delete_validation_err(key);
                add_validation_err(key,"この文字数は " + value + "文字以下でなければなりません。");
                highlight_input(key);
            }
        }
    }
    function get_ope_time(start,end){
        var ope_time = end.getTime() - start.getTime();
        ope_time = ope_time/(60*1000)
        return ope_time
    }
    function ope_time_is_err(ope_time,min_time){
        return (ope_time < min_time ? true : false);
    }
    function time_is_over(ope_time,def_time){
        return (ope_time > def_time ? true : false);
    }
    function output_time_err(msg,color_class){
        var text = "<span class=\"" + color_class + "\" id=\"time_error_text\"><strong>" + msg + "</strong></span>";
        $("#time_error").html(text);
        $("#time_error_row").show();
    }
    function delete_time_err(){
        $("#time_error").children("span").remove();
        $("#time_error_row").hide();
    }
    function output_in_time_err(msg,color_class){
        var text = "<span class=\"" + color_class + "\" id=\"in_time_error_text\"><strong>" + msg + "</strong></span>";
        $("#in_time_error").html(text);
        $("#in_time_error_row").show();
    }
    function delete_in_time_err(){
        $("#in_time_error").children("span").remove();
        $("#in_time_error_row").hide();
    }
    function input_color_change(field_name,color_class){
        var ids = field_name.split(",");
        for(var id in ids){
            $("#id_"+ids[id]).removeClass("text-body").removeClass("text-primary").removeClass("text-danger");
            $("#id_"+ids[id]).addClass(color_class);
        }
    }
    function highlight_input(field_name){
        var ids = field_name.split(",");
        for(var id in ids){
            $("#id_"+ids[id]).addClass("is-invalid");
        }
    }
    function remove_highlight(field_name){
        var ids = field_name.split(",");
        for(var id in ids){
            $("#id_"+ids[id]).removeClass("is-invalid");
        }
    }
    function add_validation_err(field_name,msg){
        var id_name = "error_1_id_" + field_name;
        text = "<span class=\"add_invalid_feedback\" id=\"" + id_name +"\"><strong>" + msg + "</strong></span>"; 
        $("#id_"+ field_name).after(text);
    }
    function delete_validation_err(field_name){
        var ids = field_name.split(",");
        for(var id in ids){
            var id_name = "error_1_id_" + ids[id];
            $("#"+id_name).remove();
        }
    }
    function onload_in_time_change(){
        //strのTrueしか反応しない
        if($('#id_mix_reverse').val()=="True"){
             $('#col_intime_label2').insertBefore('#col_intime_label1');
            $('#col_intime2').insertBefore('#col_intime1');
            $('#id_mix_reverse').prop('checked',true);
            $('#id_mix_reverse').val(true);
        }
    }
    function in_time_change(){
        //逆順の場合
        if($('#id_mix_reverse').prop('checked')==true){
            $('#col_intime_label2').insertAfter('#col_intime_label1');
            $('#col_intime2').insertAfter('#col_intime1');
            $('#id_mix_reverse').prop('checked',false);
            $('#id_mix_reverse').val(false);
        }else{
            $('#col_intime_label2').insertBefore('#col_intime_label1');
            $('#col_intime2').insertBefore('#col_intime1');
            $('#id_mix_reverse').prop('checked',true);
            $('#id_mix_reverse').val(true);
        }
    }
    function destination_check(){
        //行先入力が必須の場合のみチェック
        if($("#id_destination").prop("required")==true){
            if($("#id_destination").val()==""){
                highlight_input("destination");
                msg="行先を入力してください。"
                var text = "<span class=\"text-danger\" id=\"att_for_destination\"><strong>" + msg + "</strong></span>";
                $("#att_for_destination").html(text);
            }else{
                remove_highlight("destination");
                $("#att_for_destination").children("span").remove();
            }   
        }
    }
    function communicate_check(){
        if($("#sche_conf .text-primary").length>0){       
            //入力必須にする。
            $("#id_communicate").prop("required",true);
            if($("#id_communicate").val()==""){
                highlight_input("communicate");
                var text="<strong class=\"text-danger\">こちらに変更理由と変更後の<br class=\"d-md-none\">サービス名の入力をお願いします。</strong>"
                $("#att_for_commni").html(text);
            }else{
                if($("#id_communicate").val().length > 200){
                    highlight_input("communicate");
                    var text="<strong class=\"text-danger\">200文字以内でお願いします。</strong>"
                    $("#att_for_commni").html(text);
                }else{
                    remove_highlight("communicate");
                    $("#att_for_commni").html("");
                }
            }            
        }else{
            $("#id_communicate").removeAttr('required');
            $("#att_for_commni").html("");            
            remove_highlight("communicate");
        }
    }
    function biko_check(){
        if($("#id_biko").val()==""){
            highlight_input("biko");
            var text="<strong class=\"text-danger\">特記・連絡事項の入力は必須となります。</strong>"
            $("#att_for_biko").html(text);
        }else{
            if($("#id_biko").val().length > 200){
                highlight_input("biko");
                var text="<strong class=\"text-danger\">200文字以内でお願いします。</strong>"
                $("#att_for_biko").html(text);
            }else{
                remove_highlight("biko");
                $("#att_for_biko").html("");
            }
        }    
    }
    function submit_check(){
        if($(".is-invalid").length>0){
            var text = "<span class=\"text-danger\"><strong>入力に不備があります。<br>赤い部分をご確認下さい。</strong></span>"
            $("#submit_error").html(text);
            $("#submit_btn").prop("disabled",true);
        }else{
            $("#submit_btn").prop("disabled",false);
            $("#submit_error").html("");
        }        
    }
});