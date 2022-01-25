$(function() {
    //サービス日付入力欄を消す
    //$('#id_service_in_date_0').hide();
    //$('#id_service_out_date_0').hide();

    $('#id_deposit,#id_payment').change(function() {
        var otsuri = $('#id_deposit').val() - $('#id_payment').val()
        $('#otsuri').text(otsuri + "円");
    });
    
    var msg;
    
    $('#id_service_in_date_0,#id_service_out_date_0,#id_service_in_date_1,#id_service_out_date_1,#id_in_time_main,#id_in_time_sub').blur(function(){
        var start = new Date($('#id_service_in_date_0').val()  + " " + $('#id_service_in_date_1').val());
        var end   = new Date($('#id_service_out_date_0').val() + " " + $('#id_service_out_date_1').val());
        var min_time = Number($('#min_time').val());
        var def_time = Number($('#time').val());
        var ope_time = get_ope_time(start,end);
        var in_time_main = $('#id_in_time_main').val();
        var in_time_sub  = $('#id_in_time_sub').val();

        input_color_change("#id_service_in_date_1,#id_service_out_date_1","text-body");
        input_color_change("#id_in_time_main,#id_in_time_sub","text-body");
        delete_time_err();
        delete_in_time_err();
  
        //複合サービスの場合上書き
        if(min_time==0){
            min_time = Number($('#min_time_main').val()) + Number($('#min_time_sub').val());
        }
        if(start>=end){
            msg = "日時の入力を確認してください。";
            output_time_err(msg,"text-danger");
            input_color_change("#id_service_in_date_1,#id_service_out_date_1","text-danger");
        }else{
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
                //alert("ope=" + ope_time +" main=" + in_time_main + " sub=" + in_time_sub);
                msg="内訳の時間配分を確認して下さい。";
                output_in_time_err(msg,"text-danger");
                input_color_change("#id_in_time_main,#id_in_time_sub","text-danger");
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
                    msg = "サービス内訳が必要最低時間未満です。。";
                    output_in_time_err(msg,"text-primary");
                    input_color_change("#id_in_time_sub","text-primary");
                }
            }
        }
    });

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
        $("#time_error").append(text);
        $("#time_error_row").show();
    }
    function delete_time_err(){
        $("#time_error").children("span").remove();
        $("#time_error_row").hide();
    }
    function output_in_time_err(msg,color_class){
        var text = "<span class=\"" + color_class + "\" id=\"in_time_error_text\"><strong>" + msg + "</strong></span>";
        $("#in_time_error").append(text);
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
});