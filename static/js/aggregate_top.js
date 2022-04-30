$(function() {
    $(".pop_confirm").on('click',function(){
        if(window.confirm("実行してもよろしいですか？")){
          return true;
        }else{
          return false;
        }
    });
});