# Generated by Django 5.1 on 2024-11-20 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_remove_hackathon_venue_alter_hackathon_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hackathon',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
