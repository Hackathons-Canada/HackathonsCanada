# Generated by Django 5.1 on 2024-10-28 00:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_hackathon_review_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuratorRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=255)),
                ('team_description', models.TextField()),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hackathon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hackathon')),
            ],
        ),
    ]
