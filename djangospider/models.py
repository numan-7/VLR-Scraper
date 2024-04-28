from django.db import models

# Create your models here.
class UserStats(models.Model):
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    upvote_count = models.IntegerField(default=0)
    downvote_count = models.IntegerField(default=0)
    dead_count = models.IntegerField(default=0)
    y0y_count = models.IntegerField(default=0)
    biggest_upvote = models.IntegerField()
    biggest_upvote_quote = models.TextField(max_length=4000, default = "")
    biggest_upvote_url = models.URLField(default="")
    biggest_downvote = models.IntegerField(default=0)
    biggest_downvote_quote = models.TextField(max_length=4000, default= "")
    biggest_downvote_url = models.URLField(default="")

class ScrapyTask(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True)
    task_id = models.CharField(max_length = 100)
    is_completed = models.BooleanField(default=False)