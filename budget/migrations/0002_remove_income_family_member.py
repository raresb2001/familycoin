# Generated by Django 4.1 on 2024-03-11 15:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("budget", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="income",
            name="family_member",
        ),
    ]