from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UsernameForm
from .models import UserStats, ScrapyTask
from .tasks import run_scrapy_spider
import requests

# function to check if a user exists on vlr
def user_exists(username):
    try:
        response = requests.get(f'https://www.vlr.gg/user/{username}')
        return response.status_code == 200
    except requests.RequestException:
        return False

# main view for scraping and displaying user data
def scrape_and_display(request):
    form = UsernameForm(request.POST or None)
    posts = UserStats.objects.all()
    # if a user submits the search form
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        # make sure the user exists on vlr
        if not user_exists(username):
            return render(request, 'display.html', {'form': form, 'posts': posts, 'error': True})

        # start scrapy task
        task = run_scrapy_spider.delay(username)
        # i forgot wh i deleted
        ScrapyTask.objects.all().delete()
        # yeah self explantory
        ScrapyTask.objects.update_or_create(username=username, task_id=task.id, is_completed=False)
        return HttpResponseRedirect(f'/scrape_and_display/?username={username}')

    # user just tryna see the main web page :p
    task = ScrapyTask.objects.last()
    completed = 0
    username = None
    first_time = 0
    task = ScrapyTask.objects.all()
    if task:
        latest_object = task.last()
        username = latest_object.username
        completed = 1 if latest_object.is_completed else 0
    else:
        first_time = 1

    context = {
        'form': form,
        'posts': posts,
        'username': username,
        'is_completed': completed,
        'first_time': first_time,
        'error': 0,
    }
    return render(request, 'display.html', context)

# view to update the status of a task
@csrf_exempt
def update_scrapy_status(request):
    if request.method == "POST":
        username = request.POST.get('task_id')
        is_completed = request.POST.get('is_completed') == 'True'
        ScrapyTask.objects.filter(username=username).update(is_completed=is_completed)
        return JsonResponse({"status": "updated"}, status=200)

# view to check the status of a task
@csrf_exempt
def check_scrapy_status(request, username):
    try:
        task = ScrapyTask.objects.get(username=username)
        return JsonResponse({"is_completed": task.is_completed})
    except ScrapyTask.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

# view to cancel a task
@csrf_exempt
def cancel_scrapy_task(request, username):
    if request.method == "POST":
        try:
            task = ScrapyTask.objects.get(username=username)
            celery_task = run_scrapy_spider.AsyncResult(task.task_id)
            celery_task.abort()
            task.delete()
            return JsonResponse({"status": "cancelled"}, status=200)
        except ScrapyTask.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
