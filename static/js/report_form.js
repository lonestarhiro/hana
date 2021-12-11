$(function() {
    //サービス日付入力欄を消す
    $('#id_service_in_date_0').hide();
    $('#id_service_out_date_0').hide();

    $('#id_deposit,#id_payment').change(function() {
        var otsuri = $('#id_deposit').val() - $('#id_payment').val()
        $('#otsuri').text(otsuri + "円");
    });
});