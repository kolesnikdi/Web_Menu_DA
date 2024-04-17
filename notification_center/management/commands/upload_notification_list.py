from django.core.management.base import BaseCommand
import openpyxl
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from Web_Menu_DA.constants import NOTIFICATION_NAMES
from notification_center.models import Notification


class Command(BaseCommand):
    help = 'Upload a notification list from a file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the notification list file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'rb') as file:
                workbook = openpyxl.load_workbook(file)
                worksheet = workbook.active
                keys = [cell.value.strip() for cell in worksheet[1]]

                for row in worksheet.iter_rows(min_row=2, values_only=True):
                    data_dict = {}
                    allowed_name = False
                    for key, value in zip(keys, row):
                        if allowed_name or key == 'event_name' and value in NOTIFICATION_NAMES:
                            data_dict[key] = str(value).strip()
                            allowed_name = True
                    try:
                        notification, created = Notification.objects.update_or_create(**data_dict)
                        if created:
                            notification.save()
                    except IntegrityError:
                        existing_notification = Notification.objects.get(event_name=data_dict['event_name'])
                        for key, value in data_dict.items():
                            setattr(existing_notification, key, value)
                        existing_notification.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully uploaded notification list from {file_path}.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at path: {file_path}'))
        except ValidationError as ve:
            self.stdout.write(self.style.ERROR(f'Validation error: {ve}'))
