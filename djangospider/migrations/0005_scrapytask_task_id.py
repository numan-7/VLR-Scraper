# Generated by Django 4.1.4 on 2023-11-19 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangospider', '0004_remove_scrapytask_task_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapytask',
            name='task_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
