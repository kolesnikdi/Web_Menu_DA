import datetime

from django.conf import settings

from notification_center.models import Notification
from registration.models import WebMenuUser
from notification_center.business_logic import send_email


def final_send_mail(reg_try):
    notification_msg = Notification.get_msg(event_name='registration')
    context = {  # """ more data in context to customisation email"""
        'registration_link': f'{settings.HOST}/registration/{reg_try.code}',
        'registration_link2': f'{settings.HOST}/registration/djangofunction/{reg_try.code}'
    }
    send_email.delay(notification_msg, [reg_try.email], 'registration_mail.html', context=context)


def final_creation(validated_data, reg_try):
    user = WebMenuUser.objects.create(
        mobile_phone=validated_data['mobile_phone'],
        email=reg_try.email,
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        fathers_name=validated_data['fathers_name'],
        country=validated_data['country'],
        city=validated_data['city'],
        street=validated_data['street'],
        house_number=validated_data['house_number'],
        flat_number=validated_data['flat_number'],
        passport_series=validated_data['passport_series'],
        passport_number=validated_data['passport_number'],
        passport_date_of_issue=validated_data['passport_date_of_issue'],
        passport_issuing_authority=validated_data['passport_issuing_authority'],
    )

    user.set_password(validated_data['password'])
    user.save()
    reg_try.confirmation_time = datetime.datetime.utcnow()
    reg_try.save()
    return user
