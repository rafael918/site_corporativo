from django.shortcuts import render, redirect
from base.utils import add_form_errors_to_messages
from forum.forms import PostagemForumForm
from django.contrib import messages  
from forum import models

# Create your views here.
def lista_postagem_forum(request):
    postagens = models.PostagemForum.objects.filter(ativo=True)
    context = {'postagens': postagens}
    return render(request, 'lista-postagem-forum.html', context)

def criar_postagem_forum(request):
    form = PostagemForumForm()
    if request.method == 'POST':
        form = PostagemForumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirecionar para uma página de sucesso ou fazer qualquer outra ação desejada
            messages.success(request, 'Seu Post foi cadastrado com sucesso!')
            return redirect('lista-postagem-forum')
        else:add_form_errors_to_messages(request, form)
    return render(request, 'form-postagem-forum.html', {'form': form})