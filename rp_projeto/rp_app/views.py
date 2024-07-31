from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HorasMarcadas
from django.utils import timezone

# Create your views here.
def login_text(request):
    return render(request, 'login_text.html')

def login(request):
    if request.method == "GET":
        return render(request, 'dashboard.html')
    else:
        username = request.POST.get('name')
        senha = request.POST.get('senha')

        user_login = authenticate(username=username, password=senha)

        if user_login:
            login_django(request, user_login)
        
            return render(request, 'dashboard.html')
        else:
            return HttpResponse('Username ou Senha iválidos')
            
def login_qrcode(request):
    if request.method == "POST":
        username = request.POST.get('username')

        if username:
            user = User.objects.filter(username=username).first()

            if user:
                # Se o usuário existe, faça o login
                login_django(request, user)
                return redirect('dashboard')  # Use redirect para evitar re-envio de formulário
            else:
                # Criar o usuário se ele não existir
                user = User.objects.create_user(username=username, password='1a2s2s3d')
                user.save()
                messages.success(request, 'Usuário cadastrado, faça o scan novamente')
                return redirect('login_qrcode')
        else:
            return HttpResponse('QR Code inválido')
    else:
        return render(request, 'login_qrcode.html')


    
@login_required(login_url="/")
def dashboard(request):
        return render(request, 'dashboard.html')

def marcador(request):
    if request.method == "POST":
        tipo = request.POST.get('choice_tipo')
        para_onde = request.POST.get('choice_para_onde')

        if tipo and para_onde:
            usuario = request.user
            ultima_marcacao = HorasMarcadas.objects.filter(nome_marcador=usuario).order_by('-hora_marcada').first()

            if ultima_marcacao:
                if ultima_marcacao.tipo == 'Entrada' and tipo == 'Entrada':
                    erro = "Você deve marcar uma saída antes de marcar outra entrada."
                    return render(request, 'dashboard.html', {'Erro': erro})
                elif ultima_marcacao.tipo == 'Saida' and tipo == 'Saida':
                    erro = "Você deve marcar uma entrada antes de marcar outra saída."
                    return render(request, 'dashboard.html', {'Erro': erro})               
                
            marcar = HorasMarcadas(
                nome_marcador = request.user,
                hora_marcada = timezone.now(),
                tipo = tipo,
                para_onde = para_onde
            )
            marcar.save()
            messages.success(request, 'Marcação feita com sucesso!')
            return redirect('logout')
        else:
            # Retornar um erro se os campos não estiverem preenchidos
            erro = "Preencha todos os campos para proseguir!"
            return render(request, 'dashboard.html', {'Erro': erro})
    else:
        erro = "Envie o formulario novamente"
        return  render(request, 'dashboard.html', {'Erro': erro})

@login_required(login_url="/")
def minha_marcacao(request):
    # Buscar todas as marcações do usuário logado
    usuario = request.user
    pontos = HorasMarcadas.objects.filter(nome_marcador=usuario).order_by('-hora_marcada')

    # Organizar as marcações por data
    dados = {}
    for ponto in pontos:
        data = ponto.hora_marcada.date()
        if data not in dados:
            dados[data] = []
        dados[data].append(ponto)

    return render(request, 'minha_marcacao.html', {'dados': dados})

@login_required(login_url="/")
def logout(request):
    auth_logout(request)
    return redirect('login_qrcode')