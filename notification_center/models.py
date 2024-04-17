import logging

from django.db import models
from django.utils.translation import activate, gettext as _

from Web_Menu_DA.constants import Languages
logger = logging.getLogger(__name__)


class Notification(models.Model):
    event_name = models.CharField(max_length=50, unique=True, db_index=True)
    en_msg = models.CharField(max_length=400)
    ua_msg = models.CharField(max_length=400)

    @classmethod
    def get_msg(cls, event_name, user=None, payload=None, extra_payload=None):
        """
        :type language: Languages.choices
        :type event_name: str
        :type payload: dict
        :type user: User
        :type extra_payload: dict
        We use extra_payload if we have some data that need to be translated
        """
        if not (notification := cls.objects.filter(event_name=event_name).last()):
            logger.warning(f'warning problem with def get_msg().')
            return 'Something went wrong. Contact the site administrator.'
        language = Languages.UKRAINIAN
        msg = notification.ua_msg
        if user:
            language = user.system_language
            if language == Languages.ENGLISH:
                activate(language)
                username = {'username': f'{_(user.first_name)} {_(user.last_name)}'}
                msg = notification.en_msg
            else:
                username = {'username': f'{user.first_name} {user.last_name}'}
        else:
            username = {'username': 'Любий Користувач'}

        if not payload:
            if username or extra_payload:
                payload = {}
        if payload:
            payload.update(username)
            if extra_payload:
                activate(language)
                extra_payload = [_(item) for item in extra_payload]
                payload.update(extra_payload)
            return msg.format(**payload)
        return msg
