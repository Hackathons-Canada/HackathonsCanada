# Generated by Django 5.1.4 on 2025-01-02 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_hackathon_end_date_alter_hackathon_is_public_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='is_upvote',
            field=models.BooleanField(),
        ),
    ]