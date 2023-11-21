from django.db import models

# Create your models here.
class UserStats(models.Model):
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    biggest_upvote = models.IntegerField()
    biggest_upvote_url = models.URLField()

class ScrapyTask(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True)
    task_id = models.CharField(max_length = 100)
    is_completed = models.BooleanField(default=False)