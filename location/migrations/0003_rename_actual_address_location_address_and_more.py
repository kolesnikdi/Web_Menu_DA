# Generated by Django 4.1.2 on 2023-03-24 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_alter_company_email_alter_company_legal_name_and_more'),
        ('location', '0002_remove_location_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='actual_address',
            new_name='address',
        ),
        migrations.AlterField(
            model_name='location',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='location', to='company.company'),
        ),
    ]
