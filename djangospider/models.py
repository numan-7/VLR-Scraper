from django.db import models

# Create your models here.
class UserStats(models.Model):
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    biggest_upvote = models.IntegerField()
    biggest_upvote_quote = models.TextField(max_length=4000, default = "")
    biggest_upvote_url = models.URLField()
    biggest_downvote = models.IntegerField()
    biggest_downvote_quote = models.TextField(max_length=4000, default= "")
    biggest_downvote_url = models.URLField()

class ScrapyTask(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True)
    task_id = models.CharField(max_length = 100)
    is_completed = models.BooleanField(default=False)