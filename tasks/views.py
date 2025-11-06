from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import datetime


# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'registro.html', {
            'form': UserCreationForm()
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'registro.html', {
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'
                })
        else:
            return render(request, 'registro.html', {
                'form': UserCreationForm(),
                'error': 'La contraseña no coincide'
            })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, diaCompletado__isnull=True)
    
    # Agregar filtro por categoría
    opcion_filtro = request.GET.get('opcion')
    if opcion_filtro and opcion_filtro != '':
        tasks = tasks.filter(opcion=opcion_filtro)
    
    # Obtener opciones disponibles para el select
    opciones_disponibles = Task.objects.filter(user=request.user).values_list('opcion', flat=True).distinct()
    opciones_disponibles = [op for op in opciones_disponibles if op]
    
    return render(request, 'eventos.html', {
        'tasks': tasks,
        'opciones_disponibles': opciones_disponibles,
        'opcion_seleccionada': opcion_filtro
    })

@login_required
def tareas_completadas(request):
    tasks = Task.objects.filter(user=request.user, diaCompletado__isnull=False).order_by('diaCompletado')
    return render(request, 'eventos.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'crear_eventos.html', {
            'form': TaskForm()
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user

            opcion = request.POST.get('opcion')
            fecha_evento_str = request.POST.get('fecha_evento')

            if not opcion or not fecha_evento_str:
                return render(request, 'crear_eventos.html', {
                    'form': form,
                    'error': 'Por favor selecciona una opción y una fecha'
                })

            # Convertir fecha_evento de string a date
            try:
                fecha_evento = datetime.datetime.strptime(fecha_evento_str, "%Y-%m-%d").date()
            except ValueError:
                return render(request, 'crear_eventos.html', {
                    'form': form,
                    'error': 'Formato de fecha inválido'
                })

            new_task.opcion = opcion
            new_task.fecha_evento = fecha_evento

            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'crear_eventos.html', {
                'form': TaskForm(),
                'error': 'Por favor introduzca valores válidos'
            })


@login_required
def lista(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'lista.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'lista.html', {'task': task, 'form': form, 'error': "Error al actualizar trabajo"})

@login_required
def completar (request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.diaCompletado = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def eliminar_tarea (request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'inicio.html', {
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'inicio.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o Password es incorrecto'
            })
        else:
            login(request, user)
            return redirect('tasks')
