# Generated by Django 5.1 on 2024-12-05 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_remove_upvote_from_hacker_remove_upvote_hackathon_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='curatorrequest',
            name='review_status',
            field=models.CharField(blank=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending'), ('requesting_changes', 'Requesting Changes')], default='pending', help_text='Status of the review process', max_length=255),
        ),
    ]