import threading
import logging
import datetime
from ipware import get_client_ip

from django.core.cache import cache

from notification_center.models import Notification
from registration.models import LoginHistory, BanHistory
from notification_center.business_logic import send_email

logger = logging.getLogger(__name__)

"""
Use if the number of QuerySets to the model database is very large (exceeds 3000 - 5000)
A custom model that breaks the received data into parts after a QuerySet to the database.
The number of records in one part is indicated in the attribute - chunksize
"""


def custom_queryset_iterator(queryset, chunksize=1000):
    current = 0
    total = queryset.count()

    while current < total:
        yield queryset[current: current + chunksize]
        current += chunksize


def get_client_ip_user_agents(request):
    client_ip, is_routable = get_client_ip(request)
    if not client_ip:
        client_ip = 'ip_unreachable'
    if not (user_agent := request.user_agent):
        user_agent = 'user_agent_unreachable'
    return client_ip, user_agent


"""
RequestTracker.
Make Uniq User identifier from ip_address + user_agent or user.id
The conditions of verification are provided from CredentialsChoices
Checks for repeated requests. Blocks access if there are more repeated requests than specified.
Makes entries in LoginHistory and BanHistory
Returns True / False.
"""


class RequestTracker:
    __slots__ = ('login', 'user_id', 'user', 'user_account_email', 'ban', 'name', 'intervals', 'fields', 'max_tries',
                 'cache_time', 'lock', 'ip_address', 'user_agent', 'data_to_find', 'current_time', 'ban_msg',
                 'error_msg', 'raw_user_agent')

    def __init__(self, request, setups, login=False):
        self.login = login
        self.user_id = None
        self.user = None
        self.user_account_email = request.data.get('email', None)
        self.ban = False
        self.name = setups.name
        self.intervals = setups.intervals
        self.fields = setups.fields
        self.max_tries = setups.tries
        self.cache_time = setups.cache_time
        self.lock = threading.Lock()  # TODO del if blocking simultaneous requests will slow down the work
        self.ip_address, self.raw_user_agent = get_client_ip_user_agents(request)
        self.user_agent = str(self.raw_user_agent)
        self.data_to_find = {}
        self.current_time = datetime.datetime.utcnow()
        self.ban_msg = {'error': f'To many tries. You are blocked'}
        self.error_msg = f'To many tries. Opportunity is blocked for {{}} minutes'

    def _save_login_false(self):
        reason_of_reject = self.name
        if self.ban:
            reason_of_reject = f'BAN_{self.name}'
        login = LoginHistory(account_id=self.user_id,
                             account_email=self.user_account_email,
                             ip_address=self.ip_address,
                             user_agent=self.user_agent,
                             reason_of_reject=reason_of_reject,
                             result=False,
                             )
        login.save()

    def _perform_ban(self):
        if instance := BanHistory.objects.filter(**self.data_to_find).last():
            interval = getattr(instance, self.fields[0])
            msg = None
            for value in self.intervals:
                if value > interval:
                    setattr(instance, self.fields[0], value)
                    setattr(instance, self.fields[1], datetime.datetime.utcnow())
                    msg = {'error': self.error_msg.format(value / 60)}
                    break
                elif value == 0:
                    self.ban = True
                    setattr(instance, self.fields[0], value)
                    setattr(instance, 'ban_time', datetime.datetime.utcnow())
                    msg = self.ban_msg
                    if self.user:
                        notification_msg = Notification.get_msg(event_name='ban_msg', user=self.user)
                        send_email.delay(notification_msg, [self.user.email], 'ban_msg.html', context=notification_msg)
            if self.login:
                self._save_login_false()
            instance.save()
            return msg

        instance = BanHistory(
            account_id=self.user_id,
            account_email=self.user_account_email,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            **dict(zip(self.fields, [self.intervals[0], datetime.datetime.utcnow()]))
        )
        instance.save()
        if self.login:
            self._save_login_false()
        return {'error': self.error_msg.format(self.intervals[0] / 60)}

    def check_ban(self, user_id=None):
        if user_id: self.user_id = user_id
        if self.user_id:
            self.data_to_find['account_id'] = self.user_id
        else:
            self.data_to_find['ip_address'] = self.ip_address
            self.data_to_find['user_agent'] = self.user_agent

        if instance := BanHistory.objects.filter(**self.data_to_find).last():
            if instance.ban_time or getattr(instance, self.fields[0]) == 0:
                return self.ban_msg
            interval = getattr(instance, self.fields[0])
            time = getattr(instance, self.fields[1]).replace(tzinfo=None)
            if (self.current_time - time).total_seconds() >= interval:
                return None
            else:
                return {'error': self.error_msg.format(interval / 60)}
        return None

    def check_duplicates(self, user=None):
        if user:
            self.user_id = user.id
            self.user = user
            self.user_account_email = user.email

        if not self.user_id:
            identifier = f"{self.ip_address}_{self.user_agent}"
        else:
            identifier = f'Tracker_{self.user_id}'
        with self.lock:
            if not (reject_msg := self.check_ban()):
                if cache_data := cache.get(identifier, None):
                    for last_request_time, repeat_count in cache_data.items():
                        if (self.current_time - last_request_time).total_seconds() <= self.cache_time:
                            if repeat_count >= self.max_tries:
                                reject_msg = self._perform_ban()
                                return reject_msg
                            existing_timeout = cache.ttl(identifier)
                            cache_set(identifier, {self.current_time: repeat_count + 1}, existing_timeout)
                        else:
                            cache_set(identifier, {self.current_time: 1}, self.cache_time)
                else:
                    cache_set(identifier, {self.current_time: 1}, self.cache_time)
            return reject_msg


def cache_set(key, value, timeout, extra=None):
    """
    :type value: dict
    :type timeout: int
    :type extra: dict
    To set extra yse only uniq keys for dict!
    """
    if extra:
        value = {**value, **extra}
    cache.set(key, value, timeout)
