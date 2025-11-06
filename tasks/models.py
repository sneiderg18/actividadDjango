from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    titulo = models.CharField(max_length=100) #Tipo texto corto
    descripcion = models.TextField(blank=True) #Tipo texto largo
    f_creacion = models.DateTimeField(auto_now_add=True) #Tipo fecha añade la fecha y hora por defecto
    diaCompletado = models.DateTimeField(null=True, blank=True)
    importante = models. BooleanField(default=False) #Evaluarlo por defecto
    user = models. ForeignKey (User, on_delete=models.CASCADE) #Enlazamos la tabla task con la talaba user-eliminado en cascada

     # NUEVOS CAMPOS:
    opcion = models.CharField(max_length=50)          # Guarda la opción del select
    fecha_evento = models.DateField()

    def __str__(self):
        return self.titulo + '- by' + self.user.username