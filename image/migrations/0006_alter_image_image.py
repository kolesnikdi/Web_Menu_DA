# Generated by Django 4.1.2 on 2023-04-01 16:42

from django.db import migrations, models
import image.models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0005_remove_image_company_remove_image_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, height_field='url_height', null=True, upload_to=image.models.user_directory_path, width_field='url_width'),
        ),
    ]
