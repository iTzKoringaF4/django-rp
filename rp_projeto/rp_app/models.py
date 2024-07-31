from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class HorasMarcadas(models.Model):
    POSTO_CHOICE_TIPO = (
        ("Entrada", "Entrada"),
        ("Saida", "saida"),
        ("Cozinha", "Cozinha"),
        ("Banheiro", "Banheiro"),
    )
    POSTO_CHOICE_ONDE = (
        ("Sala", "Sala"),
        ("Quarto", "Quarto"),
        ("Cozinha", "Cozinha"),
        ("Banheiro", "Banheiro"),
    )

    id_marcada = models.AutoField(primary_key=True)
    nome_marcador = models.ForeignKey(User, on_delete=models.CASCADE)
    hora_marcada = models.DateTimeField(default=timezone.now,help_text='Horas e minutos da marcação...', null=False, blank=False)
    tipo = models.CharField(default=' ', max_length=100, blank=False, null=False, choices=POSTO_CHOICE_TIPO)
    para_onde = models.CharField(default=' ', max_length=100, blank=False, null=False, choices=POSTO_CHOICE_ONDE)
    
    def __str__(self):
        """String for representing the Model object."""
        return f'Data: {self.hora_marcada.strftime("%d/%m/%Y")} | Login: {self.nome_marcador.username} | {self.tipo}: {self.hora_marcada.strftime("%H:%M:%S")}, em {self.para_onde}'