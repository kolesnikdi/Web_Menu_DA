# Generated by Django 4.1.2 on 2023-03-20 11:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import location.business_logic
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0002_alter_company_email_alter_company_legal_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_height', models.PositiveIntegerField(blank=True, null=True)),
                ('url_width', models.PositiveIntegerField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, height_field='url_height', null=True, upload_to=location.business_logic.user_directory_path, validators=[location.business_logic.validate_image_size], width_field='url_width')),
                ('legal_name', models.CharField(max_length=50, unique=True, verbose_name='legal_name')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(db_index=True, error_messages={'unique': 'Not a valid mobile phone. Enter again and correctly.'}, max_length=13, region='UA', unique=True)),
                ('email', models.EmailField(db_index=True, max_length=50, verbose_name='email address')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('actual_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actual_location', to='company.address')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='company', to='company.company')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]