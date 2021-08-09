from django.http import HttpResponse

def staff_new(request):
    return HttpResponse("スタッフ新規登録")

def staff_edit(request):
    return HttpResponse("スタッフ編集")

def staff_conf(request):
    return HttpResponse("スタッフ詳細")

def staff_del(request):
    return HttpResponse("スタッフ削除")
