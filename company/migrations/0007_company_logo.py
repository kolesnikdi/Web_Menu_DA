# Generated by Django 4.1.2 on 2023-03-30 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0003_auto_20230328_2129'),
        ('company', '0006_remove_company_logo_remove_company_url_height_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='company_logo', to='image.image'),
        ),
    ]
