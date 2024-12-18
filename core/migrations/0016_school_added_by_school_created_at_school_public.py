# Generated by Django 5.1 on 2024-11-27 22:21

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_alter_hackathon_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="school",
            name="added_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="schools_added",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="school",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="school",
            name="public",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Is the school public (Is displayed on fields)",
            ),
        ),
    ]
