from django.shortcuts import get_object_or_404, render
from contas.models import MyUser

def perfil_view(request, username):
    filtro = MyUser.objects.select_related('perfil').prefetch_related('user_postagem_forum')
    #perfil = get_object_or_404(MyUser.objects.select_related(filtro, username=username)
    #perfil = get_object_or_404(MyUser.objects.select_related(), filtro=filtro, username=username)
    perfil = get_object_or_404(MyUser.objects.select_related(), filtro=valor_do_filtro, username=username)


    context = {'obj': perfil} 
    return render(request, 'perfil.html', context)