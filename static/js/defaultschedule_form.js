$(function() {
    var type_select = $('#id_type').val();
    if(type_select == 0){
        $('#weekbase_container').show();
        $('#daybase_container').hide();
    }else if(type_select == 1){
        $('#weekbase_container').hide();
        $('#daybase_container').show();
    }

    var daytype_select = $('#id_day').val();
    if(daytype_select !=3){
        $('#id_day').hide();
    }else{
        $('#id_day').show();
    }

    $('#id_type').change(function() {
        type_select = $('#id_type option:selected').val();
        
        if(type==0){
            $('#weekbase_container').show();
            $('#daybase_container').hide();
            $('#id_daytype').val(0);
            $('#id_day').val("");
        }else if(type==1){
            $('#weekbase_container').hide();
            $('#daybase_container').show();
            $('#id_weektype').val(0);
            $('#id_sun').prop('checked',false);
            $('#id_mon').prop('checked',false);
            $('#id_tue').prop('checked',false);
            $('#id_wed').prop('checked',false);
            $('#id_thu').prop('checked',false);
            $('#id_fri').prop('checked',false);
            $('#id_sat').prop('checked',false);
            $('#id_wed').prop('checked',false);
        }
    })
    
    $('#id_daytype').change(function() {
        var daytype = $('#id_daytype option:selected').val();

        if(daytype !=3){
            $('#id_day').hide();
            $('#id_day').val("");
        }else{
            $('#id_day').show();
        }
    })
});