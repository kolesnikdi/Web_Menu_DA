# Generated by Django 4.1.2 on 2023-06-29 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_alter_webmenuuser_type_2fa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webmenuuser',
            name='type_2fa',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Email'), (2, 'Gauth')], default=0),
        ),
    ]
