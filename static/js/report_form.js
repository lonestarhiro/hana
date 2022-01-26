$(function() {

    main_check();
    in_time_change();
    comunicate_check();
    submit_check(); 

    $('#id_deposit,#id_payment').change(function(){
        var otsuri = $('#id_deposit').val() - $('#id_payment').val();
        $('#otsuri').text(otsuri + "円");
    });
    
    $('#mix_reverse_btn').on('click',function(){
        if($('#id_mix_reverse').prop('checked')==true){
            $('#id_mix_reverse').prop('checked',false);
        }else{
            $('#id_mix_reverse').prop('checked',true);
        }
        in_time_change();
    });

    $('#id_service_in_date_0,#id_service_out_date_0,#id_service_in_date_1,#id_service_out_date_1,#id_in_time_main,#id_in_time_sub').blur(function(){
        main_check();
    });

    function main_check(){
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
        input_color_change("#id_service_in_date_1,#id_service_out_date_1,#id_in_time_main,#id_in_time_sub","text-body");
        delete_time_err();
        delete_in_time_err();
        //送信後のバリデーションによるエラーも消す。
        $("#error_1_id_service_in_date_1,#error_1_id_service_out_date_1").hide();
        $("#error_1_id_in_time_main,#error_1_id_in_time_sub").hide();
        remove_highlight("#id_service_in_date_1,#id_service_out_date_1");
        remove_highlight("#id_in_time_main,#id_in_time_sub");
  
        //複合サービスの場合上書き
        if(min_time==0){
            min_time = Number($('#min_time_main').val()) + Number($('#min_time_sub').val());
        }
        if(start>=end){
            msg = "日時の入力を確認してください。";
            output_time_err(msg,"text-danger");
            highlight_input("#id_service_in_date_1,#id_service_out_date_1");
        }else{
            //送信後のバリデーションによるエラーも消す。
            $("#error_1_id_service_in_date,#error_1_id_service_out_date").hide();
            remove_highlight("#id_service_in_date_1,#id_service_out_date_1");

            if(ope_time_is_err(ope_time,min_time)){
                msg = "サービスの必要最低時間に達していません。";
                output_time_err(msg,"text-primary");
                input_color_change("#id_service_in_date_1,#id_service_out_date_1","text-primary");
            }
            if(time_is_over(ope_time,def_time)){
                msg = "予定サービス時間を超過しています。<br>サービスが変更された場合は<br>後程、担当者までご連絡ください。";
                output_time_err(msg,"text-primary");
                input_color_change("#id_service_in_date_1,#id_service_out_date_1","text-primary");
            }
        }
        if(typeof in_time_main !== undefined){
            var in_time_main  = Number($('#id_in_time_main').val());
            var in_time_sub   = Number($('#id_in_time_sub').val());
            var min_time_main = Number($('#min_time_main').val());
            var min_time_sub  = Number($('#min_time_sub').val());

            if(ope_time != (in_time_main + in_time_sub)){
                msg="内訳の時間配分を確認して下さい。";
                output_in_time_err(msg,"text-danger");
                highlight_input("#id_in_time_main,#id_in_time_sub");
            }else{
                if(ope_time_is_err(in_time_main,min_time_main)){
                    msg = "サービス内訳が必要最低時間未満です。";
                    output_in_time_err(msg,"text-primary");
                    input_color_change("#id_in_time_main","text-primary");
                    //$("#modal_body").html("内訳のサービスの必要最低時間に達していません。")
                    //$(".modal").modal("show");
                    //$("#id_in_time_main").addClass('text-danger');
                }
                if(ope_time_is_err(in_time_sub,min_time_sub)){
                    msg = "サービス内訳が必要最低時間未満です。";
                    output_in_time_err(msg,"text-primary");
                    input_color_change("#id_in_time_sub","text-primary");
                }
            }
        }
        comunicate_check();
        submit_check();
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
    function input_color_change(id,color_class){
        $(id).removeClass("text-body").removeClass("text-primary").removeClass("text-danger");
        $(id).addClass(color_class);
    }
    function highlight_input(id){
        $(id).addClass("is-invalid");
    }
    function remove_highlight(id){
        $(id).removeClass("is-invalid");
    }
    function in_time_change(){
        //逆順の場合
        if($('#id_mix_reverse').prop('checked')==true){
            $('#col_intime_label2').insertBefore('#col_intime_label1');
            $('#col_intime2').insertBefore('#col_intime1');
        }else{
            $('#col_intime_label2').insertAfter('#col_intime_label1');
            $('#col_intime2').insertAfter('#col_intime1');
        }
    }
    function comunicate_check(){
        if($("#sche_conf .text-primary").length>0){       
            text="<strong class=\"text-primary\">こちらに変更理由と変更後の<br class=\"d-md-none\">サービス名の入力をお願いします。</strong>"
            $("#att_for_commni").html(text);
        }else{
            $("#att_for_commni").html("");
        }
    }
    function submit_check(){
        if($("#sche_conf .is-invalid").length>0){
            $("#submit_btn").prop("disabled",true);
            var text = "<span class=\"text-danger\"><strong>時間の入力に誤りがあります。</strong></span>"
            $("#submit_error").html(text);
        }else if($("#biko").val()==""){
            $("#submit_btn").prop("disabled",true);
            var text = "<span class=\"text-danger\"><strong>特記・連絡事項欄が未入力です。</strong></span>"
            $("#submit_error").html(text);
        }else{
            $("#submit_btn").prop("disabled",false);
            $("#submit_error").html("");
        }
    }
});