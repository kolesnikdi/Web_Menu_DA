import datetime
import uuid
import re

from django.core import exceptions
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from Web_Menu_DA.constants import Types2FA, Languages
from registration.managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField


class RegistrationTry(models.Model):
    email = models.EmailField(unique=True, db_index=True, max_length=254,
                              error_messages={'unique': 'Not a valid email. Enter again and correctly.'})
    code = models.UUIDField(db_index=True, default=uuid.uuid4)
    creation_time = models.DateTimeField(default=datetime.datetime.utcnow)
    confirmation_time = models.DateTimeField(null=True)


def custom_validate_password(password):
    """
    Here due to the circular import
    Check if this password contain uppercase letters, lowercase letters, numbers, and symbols
    :type password: accounts.models.User.password
    """
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).*$'
    if bool(re.search(pattern, password)):
        return
    raise exceptions.ValidationError('Must contain uppercase letters, lowercase letters, numbers, and symbols')


class WebMenuUser(AbstractBaseUser, PermissionsMixin):

    username = None
    mobile_phone = PhoneNumberField(region='UA', max_length=13, unique=True, db_index=True,
                                    error_messages={'unique': 'Not a valid mobile phone. Enter again and correctly.'})
    first_name = models.CharField('first name', max_length=30, null=True)
    last_name = models.CharField('last name', max_length=30, null=True)
    fathers_name = models.CharField('fathers name', max_length=20)
    country = models.CharField('country', max_length=30)
    city = models.CharField('city', max_length=30)
    street = models.CharField('street', max_length=50)
    house_number = models.CharField('house number', max_length=10)
    flat_number = models.CharField('flat number', max_length=10)
    passport_series = models.CharField('passport series', max_length=2)
    passport_number = models.CharField('passport number', max_length=6)
    passport_date_of_issue = models.DateField('passport date of issue', null=True)
    passport_issuing_authority = models.CharField('passport issuing authority', max_length=100)
    email = models.EmailField(verbose_name='email address', unique=True, db_index=True, max_length=254,
                              error_messages={'unique': 'Not a valid email. Enter again and correctly.'})
    password = models.CharField('password', max_length=88, validators=[MinLengthValidator(8), custom_validate_password])
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    type_2fa = models.PositiveSmallIntegerField(choices=Types2FA.choices, default=Types2FA.DISABLED)
    system_language = models.CharField(max_length=2, choices=Languages.choices, default=Languages.UKRAINIAN)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()   # """ Need to createsuperuser"""

    def __str__(self):
        return self.email


class LoginHistory(models.Model):
    account = models.ForeignKey('registration.WebMenuUser', related_name='login_history', on_delete=models.CASCADE, null=True)
    account_email = models.CharField('email', max_length=254, db_index=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=False)
    user_agent = models.CharField(max_length=400, blank=False)
    reason_of_reject = models.CharField(max_length=150, null=True)
    result = models.BooleanField(default=False)
    result_time = models.DateTimeField(default=datetime.datetime.utcnow)


class BanHistory(models.Model):
    account = models.ForeignKey('registration.WebMenuUser', related_name='ban', on_delete=models.CASCADE, null=True)
    account_email = models.CharField('email', max_length=254, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=False)
    user_agent = models.CharField(max_length=400, blank=False)
    credentials_interval = models.IntegerField(null=True)
    credentials_tries_time = models.DateTimeField(null=True)
    cache_endpoint_interval = models.IntegerField(null=True)
    cache_endpoint_tries_time = models.DateTimeField(null=True)
    ban_time = models.DateTimeField(null=True)
