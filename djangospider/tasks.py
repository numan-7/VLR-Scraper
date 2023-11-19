from celery import shared_task
import subprocess

@shared_task
def run_scrapy_spider(username):
    subprocess.Popen(['scrapy', 'crawl', 'vlr', '-a', f'username={username}'])