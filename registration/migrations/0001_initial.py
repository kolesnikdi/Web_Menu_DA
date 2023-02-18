# Generated by Django 4.1.2 on 2023-02-08 15:50

from django.db import migrations, models
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationTry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, error_messages={'unique': 'Not a valid email. Enter again and correctly.'}, max_length=254, unique=True)),
                ('code', models.UUIDField(db_index=True, default=uuid.uuid4)),
                ('creation_time', models.DateTimeField(auto_now=True)),
                ('confirmation_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebMenuUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('mobile_phone', phonenumber_field.modelfields.PhoneNumberField(db_index=True, error_messages={'unique': 'Not a valid mobile phone. Enter again and correctly.'}, max_length=13, region='UA', unique=True)),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, null=True, verbose_name='last name')),
                ('fathers_name', models.CharField(max_length=20, verbose_name='fathers name')),
                ('country', models.CharField(max_length=30, verbose_name='country')),
                ('city', models.CharField(max_length=30, verbose_name='city')),
                ('street', models.CharField(max_length=50, verbose_name='street')),
                ('house_number', models.CharField(max_length=10, verbose_name='house number')),
                ('flat_number', models.CharField(max_length=10, verbose_name='flat number')),
                ('passport_series', models.CharField(max_length=2, verbose_name='passport series')),
                ('passport_number', models.CharField(max_length=6, verbose_name='passport number')),
                ('passport_date_of_issue', models.DateField(verbose_name='passport date of issue')),
                ('passport_issuing_authority', models.CharField(max_length=100, verbose_name='passport issuing authority')),
                ('email', models.EmailField(db_index=True, error_messages={'unique': 'Not a valid email. Enter again and correctly.'}, max_length=254, unique=True, verbose_name='email address')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]