import openpyxl

from django.db import IntegrityError
from rest_framework import serializers

from Web_Menu_DA.constants import NOTIFICATION_NAMES
from notification_center.models import Notification


class NotificationSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        uploaded_file = validated_data.get('file')
        if not uploaded_file:
            raise serializers.ValidationError('Upload file according to the terms of use')
        try:
            workbook = openpyxl.load_workbook(uploaded_file)
            worksheet = workbook.active
            keys = [cell.value.strip() for cell in worksheet[1]]

            for row in worksheet.iter_rows(min_row=2, values_only=True):
                data_dict = {}
                allowed_name = False
                for key, value in zip(keys, row):
                    if allowed_name or key == 'event_name' and value in NOTIFICATION_NAMES:
                        data_dict[key] = str(value).strip()
                        allowed_name = True
                    else:
                        raise serializers.ValidationError('Upload file according to the terms of use')
                try:
                    notification, created = Notification.objects.update_or_create(**data_dict)
                    if created:
                        notification.save()
                except IntegrityError:
                    existing_notification = Notification.objects.get(event_name=data_dict['event_name'])
                    for key, value in data_dict.items():
                        setattr(existing_notification, key, value)
                    existing_notification.save()
            return notification
        except Exception:
            raise serializers.ValidationError('Upload file according to the terms of use')
