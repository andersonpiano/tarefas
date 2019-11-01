from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from .forms import TaskForm
from django.contrib import messages
import datetime
from django.views.generic import TemplateView

from .models import Task

@login_required
def taskList(request):
    
    search = request.GET.get('search')
    filter = request.GET.get('filter')
    tasksDoneRecently = Task.objects.filter(done='feito', updated_at__gt=datetime.datetime.now()-datetime.timedelta(days=7), user=request.user).count()
    tasksDone = Task.objects.filter(done='feito', user=request.user).count()
    tasksDoing = Task.objects.filter(done='fazendo', user=request.user).count()
    tasksTodo = Task.objects.filter(done='fazer', user=request.user).count()

    if search:
        tasks = Task.objects.filter(title__icontains=search, user=request.user)
    elif filter:
        tasks = Task.objects.filter(done=filter)
    else:
        tasks_list = Task.objects.all().order_by('-created_at').filter(user=request.user)

        paginator = Paginator(tasks_list, 10)

        page = request.GET.get('page')
        tasks = paginator.get_page(page)

    return render(request, 'tasks/list.html', 
        {'tasks':tasks, 'tasksrecently': tasksDoneRecently, 'tasksdone': tasksDone, 'tasksdoing': tasksDoing, 'taskstodo': tasksTodo  })

@login_required
def taskView(request, id):
    task = get_object_or_404(Task, pk=id)
    return render(request, 'tasks/task.html', {'task': task})

@login_required
def newTask(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            task.done = 'fazer'
            task.user = request.user
            task.save()
            return redirect('/')
    else:
        form = TaskForm()
        return render(request, 'tasks/addtask.html', {'form': form})

@login_required
def editTask(request, id):
    task = get_object_or_404(Task, pk=id)
    form = TaskForm(instance=task)

    if(request.method == 'POST'):
        form = TaskForm(request.POST, instance=task)

        if(form.is_valid()):
            task.save()
            return redirect('/')
        else:
            return render(request, 'task/edittask.html', {'form': form, 'task': task})
    else:
        return render(request, 'tasks/edittask.html', {'form': form, 'task': task})

@login_required
def deleteTask(request, id):
    task = get_object_or_404(Task, pk=id)
    task.delete()

    messages.info(request, 'Tarefa deletada com sucesso.')

    return redirect('/')

@login_required
def changeStatus(request, id):
    task = get_object_or_404(Task, pk=id)

    if(task.done == 'fazer'):
        task.done = 'fazendo'
    else:
        task.done = 'feito'

    task.save()

    return redirect('/')

@login_required
def helloWorld(request):
    return HttpResponse('Hello World!')
    
@login_required
def yourName(request, name):
    return render(request, 'tasks/yourname.html', {'name':name})

class Sandro (TemplateView):
    template_name = 'base.html'
    
    def get_context_data(self, **kwargs):
        tasksDone = Task.objects.get(done='feito')
        context = super().get_context_data(**kwargs)
        context['tasks'] = tasksDone.title
        return context