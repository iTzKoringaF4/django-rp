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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Create your views here.
def login_text(request):
    return render(request, 'login_text.html')
#-----------------------------------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------------------------------            

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

 #-----------------------------------------------------------------------------------------------------------------------   

@login_required(login_url="/")
def dashboard(request):
        return render(request, 'dashboard.html')

#-----------------------------------------------------------------------------------------------------------------------

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
    
#-----------------------------------------------------------------------------------------------------------------------

@login_required(login_url="/")
def minha_marcacao(request):
    # Buscar todas as marcações do usuário logado com um limite de 5
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

#-----------------------------------------------------------------------------------------------------------------------

@login_required(login_url="/")
def filtro_de_data(request):
    data = request.GET.get('data')
    usuario = request.user
    if data:
        pontos = HorasMarcadas.objects.filter(nome_marcador=usuario, hora_marcada__date=data).order_by('-hora_marcada')
    else:
        pontos = HorasMarcadas.objects.filter(nome_marcador=usuario).order_by('-hora_marcada')[:5]

    dados = {}
    for ponto in pontos:
        data = ponto.hora_marcada.date()
        if data not in dados:
            dados[data] = []
        dados[data].append(ponto)

    return render(request, 'minha_marcacao.html', {'dados': dados})

#-----------------------------------------------------------------------------------------------------------------------

@login_required(login_url="/")
def logout(request):
    auth_logout(request)
    return redirect('login_qrcode')

#-----------------------------------------------------------------------------------------------------------------------

def exportar_para_google_sheets(request):
    # Obter o caminho absoluto para o arquivo de credenciais
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(BASE_DIR, 'static', 'cred.json')
    
    # Configurar as credenciais
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    # Especificar a URL ou o ID da planilha
    # Você pode usar a URL completa da planilha:
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1t07F1k_lgrsc-7K9hRWyiaCgX5hoj7wj-2CuDoY15-o/edit?usp=sharing')
    # Ou usar o ID da planilha:
    #spreadsheet = client.open_by_key('SEU_ID_AQUI')
    
    # Abrir a primeira aba da planilha
    sheet = spreadsheet.sheet1

    # Obter os dados do banco de dados e agrupar por nome e data
    marcacoes = HorasMarcadas.objects.all().order_by('nome_marcador', 'hora_marcada')
    
    # Preparar os dados para a planilha
    data = [["Nome", "Tipo", "Hora Marcada", "Para Onde", "Tipo", "Hora Marcada", "De Onde"]]
    
    paired_data = []
    for i in range(0, len(marcacoes), 2):
        if i + 1 < len(marcacoes):
            entrada = marcacoes[i]
            saida = marcacoes[i + 1]
            if entrada.nome_marcador == saida.nome_marcador:
                paired_data.append([
                    entrada.nome_marcador.username,
                    entrada.tipo,
                    entrada.hora_marcada.strftime("%d/%m/%Y %H:%M:%S"),
                    entrada.para_onde,
                    saida.tipo,
                    saida.hora_marcada.strftime("%d/%m/%Y %H:%M:%S"),
                    saida.para_onde,
                ])
    
    # Limpar a planilha existente
    sheet.clear()

    # Inserir os novos dados
    if paired_data:
        sheet.insert_rows(data + paired_data, 1)

    return HttpResponse("Dados exportados para o Google Sheets com sucesso!")