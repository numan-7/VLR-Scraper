import subprocess, time
from celery.contrib.abortable import AbortableTask
from djangospider.celery import app

@app.task(bind=True, base=AbortableTask)
def run_scrapy_spider(self, username):
    process = subprocess.Popen(['scrapy', 'crawl', 'vlr', '-a', f'username={username}'])
    while True:
        if self.is_aborted():
            process.kill()
            return True
        elif process.poll() is not None:
            break
        time.sleep(.25)