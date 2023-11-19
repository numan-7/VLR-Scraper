from django.shortcuts import render, HttpResponseRedirect
from .forms import UsernameForm
from .models import UserStats
from .tasks import run_scrapy_spider
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ScrapyTask
import requests
from django.contrib import messages

def user_exists(username):
    try:
        response = requests.get(f'https://www.vlr.gg/user/{username}')
        return response.status_code == 200
    except requests.RequestException:
        return False

def scrape_and_display(request):
    form = UsernameForm(request.POST or None)
    posts = UserStats.objects.all()

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        if not user_exists(username):
            context = {
                'form': form,
                'posts': posts,
                'error': 1,
            }            
            return render(request, 'display.html', context)
        task = run_scrapy_spider.delay(username)
        ScrapyTask.objects.all().delete()
        ScrapyTask.objects.update_or_create(task_id=username, defaults={'is_completed': False})
        return HttpResponseRedirect('/scrape_and_display/?task_id=' + username)
    
    completed = 0
    task_id = None
    first_time = 0
    task = ScrapyTask.objects.all()
    if task:
        latest_object = task.last()
        task_id = latest_object.task_id
        completed = 1 if latest_object.is_completed else 0
    else:
        first_time = 1
    print(posts)
    context = {
        'form': form,
        'posts': posts,
        'task_id': task_id,
        'is_completed': completed,
        'first_time': first_time
    }
    return render(request, 'display.html', context)

@csrf_exempt
def update_scrapy_status(request):
    if request.method == "POST":
        task_id = request.POST.get('task_id')
        is_completed = request.POST.get('is_completed') == 'True'
        ScrapyTask.objects.update_or_create(task_id=task_id, defaults={'is_completed': is_completed})
        return JsonResponse({"meow": "meow"}, status=200)
    
def check_scrapy_status(request, task_id):
    try:
        task = ScrapyTask.objects.get(task_id=task_id)
        return JsonResponse({"is_completed": task.is_completed})
    except ScrapyTask.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)