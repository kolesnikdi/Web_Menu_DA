from django.db import models


class Measures(models.IntegerChoices):  # or class Measures(IntEnum): from enum import IntEnum # activate 21 str
    milligrams = 0
    grams = 1
    pieces = 2


class Types2FA(models.IntegerChoices):
    DISABLED = 0
    EMAIL = 1
    GAUTH = 2


class CredentialsChoices:
    """self.intervals = 0 = BAN"""

    class Value:
        __slots__ = ('name', 'tries', 'cache_time', 'intervals', 'fields')

        def __init__(self, name, tries, cache_time, intervals, fields):
            self.name = name
            self.tries = tries
            self.cache_time = cache_time  # in seconds
            self.intervals = intervals  # in seconds
            self.fields = fields

    login = Value('credentials', 2, 24 * 60 * 60, (30, 120, 300, 600, 0),
                  ('credentials_interval', 'credentials_tries_time'))
    registration = Value('registration', 2, 24 * 60 * 60, (30, 120, 300, 600, 0),
                         ('registration_interval', 'registration_tries_time'))
    cache_endpoint = Value('fraud', 3, 120, (120, 300, 600, 0),
                           ('cache_endpoint_interval', 'cache_endpoint_tries_time'))


class Languages(models.TextChoices):
    ENGLISH = 'en'
    UKRAINIAN = 'ua'


NOTIFICATION_NAMES = [
    'ban_msg',
    'registration',
]
