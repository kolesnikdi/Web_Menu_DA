# Generated by Django 4.1.2 on 2023-03-22 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='owner',
        ),
    ]
