# Generated by Django 4.1.2 on 2023-03-28 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0005_alter_location_address'),
        ('address', '0001_initial'),
        ('company', '0003_alter_company_actual_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='actual_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='actual_address', to='address.address'),
        ),
        migrations.AlterField(
            model_name='company',
            name='legal_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='legal_address', to='address.address'),
        ),
    ]
