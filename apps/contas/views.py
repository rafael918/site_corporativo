from django.contrib.auth.models import Group, User
from atexit import register
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from base.utils import add_form_errors_to_messages
from core import settings
from perfil.forms import PerfilForm
from perfil.models import Perfil
from contas.permissions import grupo_colaborador_required
from contas.models import MyUser
from contas.forms import CustomUserCreationForm, UserChangeForm


# Rota Timeout (Desconecta por inatividade)
def timeout_view(request):
    return render(request, 'timeout.html')

def logout_view(request):
    logout(request)
    return redirect('home')


# Mudança de Senha Force (first_login)
@login_required
def force_password_change_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.force_change_password = False  # passa o parâmetro para False.
            user.save()
            update_session_auth_hash(request, user)
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form': form}
    return render(request, 'registration/password_force_change_form.html', context)


# Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_authenticated and user.requires_password_change():  # Verifica
                msg = ('Olá ' + user.first_name + ', como você pode perceber atualmente '
                    'a sua senha é 123 cadastrado. Recomendamos fortemente '
                    'que você altere sua senha para garantir a segurança da sua conta. '
                    'É importante escolher uma senha forte e única que não seja fácil de adivinhar. '
                    'Obrigado pela sua atenção!')
                messages.warning(request, msg)
                return redirect('force_password_change')  # Vai para rota de alterar senha.
            else:
                return redirect('home')
        else:
            messages.error(request, 'Se o erro persistir, entre em contato com o administrador do sistema.')

    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')


# Register
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, user=request.user)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_valid = False
            usuario.is_active = False  # adiciona isso.
            usuario.save()
            
            group = Group.objects.get(name='usuario')
            usuario.groups.add(group)
            
            Perfil.objects.create(usuario=usuario)  # cria instância perfil do usuário
            
            # Envia e-mail para usuário
            send_mail(  # Envia email para usuario
                'Cadastro Plataforma',
                f'Olá, {usuario.first_name}, em breve você receberá um e-mail de '
                'aprovação para usar a plataforma.',
                settings.DEFAULT_FROM_EMAIL,  # De (em produção usar o e-mail que está no settings)
                [usuario.email],  # para
                fail_silently=False,
            )
            
            messages.success(request, 'Registrado. Um e-mail foi enviado para o administrador aprovar. Aguarde contato')
            return redirect('login')
        else:
            # Tratar quando usuario já existe, senhas, etc.
            messages.error(request, 'A senha deve ter pelo menos 1 caractere maiúsculo, 1 caractere especial e no mínimo 8 caracteres.')
    form = CustomUserCreationForm(user=request.user)
    return render(request, "registration/register.html", {"form": form})


# Atualizar meu usuário 
from django.core.paginator import Paginator

@login_required
@grupo_colaborador_required(['administrador','colaborador'])
def lista_usuarios(request):
    lista_usuarios = MyUser.objects.select_related('perfil').filter(is_superuser=False)
    paginacao = Paginator(lista_usuarios, 3)
    pagina_numero = request.GET.get("page")
    page_obj = paginacao.get_page(pagina_numero)
    context = {'page_obj': page_obj}
    return render(request, 'lista-usuarios.html', context)

# Atualizar qualquer usuário pelo parâmetro username
@login_required
@grupo_colaborador_required(['administrador', 'colaborador'])
def atualizar_usuario(request, username):
    user = get_object_or_404(MyUser, username=username)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user, user=request.user)
        if form.is_valid():
            form.save()
            if user.is_active:  # se usuario for ativado, muda o status para True e envia e-mail
                user.is_active = True  # muda status para True (Aprovado)
                print(user.is_active)
                # Envia e-mail avisando usuário.
                send_mail(  # Envia email para usuario
                    'Cadastro Aprovado',
                    f'Olá, {user.first_name}, seu e-mail foi aprovado na plataforma.',
                    settings.DEFAULT_FROM_EMAIL,  # De (em produção usar o e-mail que está no settings)
                    [user.email],  # para
                    fail_silently=False,
                )
                messages.success(request, 'O usuário ' + user.email + ' foi atualizado com sucesso!')
                return redirect('lista_usuarios')
            user.save()
            messages.success(request, 'O perfil de usuário foi atualizado com sucesso!')
            return redirect('home')
        else:
            add_form_errors_to_messages(request, form)
    else:
        form = UserChangeForm(instance=user, user=request.user)
    return render(request, 'user_update.html', {'form': form})


# Lista de todos os usuários do  sistema
from django.core.paginator import Paginator

@login_required
@grupo_colaborador_required(['administrador','colaborador'])
def lista_usuarios(request):
    lista_usuarios = MyUser.objects.select_related('perfil').filter(is_superuser=False)
    paginacao = Paginator(lista_usuarios, 5)
    pagina_numero = request.GET.get("page")
    page_obj = paginacao.get_page(pagina_numero)
    context = {'page_obj': page_obj}
    return render(request, 'lista-usuarios.html', {'page_obj'})


@login_required
@grupo_colaborador_required(['administrador', 'colaborador'])
def adicionar_usuario(request):
    user_form = CustomUserCreationForm(user=request.user)
    perfil_form = PerfilForm(user=request.user)

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, user=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, user=request.user)

        if user_form.is_valid() and perfil_form.is_valid():
            # Salve o usuário
            usuario = user_form.save()
            
            group = Group.objects.get(name='usuario')
            usuario.groups.add(group)

            # Crie um novo perfil para o usuário
            perfil = perfil_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            messages.success(request, 'Usuário adicionado com sucesso.')
            return redirect('lista_usuarios')
        else:
            # Adicionar mensagens de erro aos campos dos formulários
            add_form_errors_to_messages(request, user_form)
            add_form_errors_to_messages(request, perfil_form)
                    
    context = {'user_form': user_form, 'perfil_form': perfil_form}
    return render(request, "adicionar-usuario.html", context)




