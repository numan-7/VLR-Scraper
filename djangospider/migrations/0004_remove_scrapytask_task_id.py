# Generated by Django 4.1.4 on 2023-11-18 23:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangospider', '0003_scrapytask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scrapytask',
            name='task_id',
        ),
    ]