# Generated by Django 4.1.2 on 2023-03-28 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=30, verbose_name='legal country')),
                ('city', models.CharField(max_length=30, verbose_name='legal city')),
                ('street', models.CharField(max_length=50, verbose_name='legal street')),
                ('house_number', models.CharField(max_length=10, verbose_name='legal house number')),
                ('flat_number', models.CharField(max_length=10, verbose_name='legal flat number')),
            ],
        ),
    ]
