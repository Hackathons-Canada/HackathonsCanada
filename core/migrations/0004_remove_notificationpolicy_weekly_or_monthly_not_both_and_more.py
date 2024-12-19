# Generated by Django 5.0.4 on 2024-07-04 13:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_notificationpolicy_alter_hacker_managers_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="notificationpolicy",
            name="weekly_or_monthly_not_both",
        ),
        migrations.AddField(
            model_name="hackathon",
            name="metadata",
            field=models.JSONField(
                blank=True,
                help_text="Metadata about the source of the hackathon",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="hackathon",
            name="source",
            field=models.CharField(
                choices=[("SCR", "Scrapped"), ("USR", "User Submitted")],
                default="USR",
                max_length=3,
            ),
        ),
    ]