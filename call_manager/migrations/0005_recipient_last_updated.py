# Generated by Django 4.2.5 on 2023-09-14 17:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("call_manager", "0004_recipient_call_back_time_alter_recipient_call_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipient",
            name="last_updated",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
