from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from .forms import UsernameForm
from .models import UserStats
from .tasks import run_scrapy_spider
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ScrapyTask

def scrape_and_display(request):
    form = UsernameForm(request.POST or None)
    posts = UserStats.objects.all()
    task_id = request.GET.get('task_id')
    task_status = None

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        task = run_scrapy_spider.delay(username)
        ScrapyTask.objects.update_or_create(task_id=username, defaults={'is_completed': False})
        return HttpResponseRedirect('/scrape_and_display/?task_id=' + username)

    if task_id:
        try:
            task = ScrapyTask.objects.get(task_id=task_id)
            task_status = task.is_completed
        except ScrapyTask.DoesNotExist:
            task_status = 'not_found'
    context = {
        'form': form,
        'posts': posts,
        'task_id': task_id,
        'task_status': task_status
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