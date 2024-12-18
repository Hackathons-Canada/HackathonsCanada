# Generated by Django 5.1.4 on 2024-12-18 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_alter_hackathon_duplication_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hackathon',
            name='duplication_id',
            field=models.CharField(blank=True, help_text='Duplication ID for the Hackathon', max_length=255, null=True, unique=True),
        ),
    ]
