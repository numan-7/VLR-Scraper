# Generated by Django 4.1.4 on 2023-11-21 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangospider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstats',
            name='biggest_downvote_quote',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='userstats',
            name='biggest_upvote_quote',
            field=models.CharField(default='', max_length=150),
        ),
    ]
