# Generated by Django 5.1.4 on 2024-12-18 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_alter_hackathon_duplication_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hackathon',
            name='count_downvotes',
        ),
        migrations.RemoveField(
            model_name='hackathon',
            name='count_upvotes',
        ),
        migrations.AddField(
            model_name='hackathon',
            name='count_votes',
            field=models.BigIntegerField(default=0),
        ),
    ]
