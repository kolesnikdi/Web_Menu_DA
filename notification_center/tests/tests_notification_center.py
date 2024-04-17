from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status

from Web_Menu_DA import settings
from notification_center.models import Notification


class TestNotificationUploadView:

    def test_upload_notification_list_valid(self, authenticated_client):
        authenticated_client.user.is_staff = True
        authenticated_client.user.save()
        file_path = str(settings.BASE_DIR) + r'\notification_center\tests\notification_list.xlsx'
        file = SimpleUploadedFile(
            name='notification_list.xlsx',
            content=open(file_path, 'rb').read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response = authenticated_client.post(reverse('notificationlist'), data={'file': file}, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json['upload'] == 'You have successfully updated the list of notifications.'
        data_for_check = Notification.objects.all()
        assert data_for_check[0].en_msg == '{username} your account has been banned. For more information, please contact Support'
        assert data_for_check[1].en_msg == '{username} follow the links provided in the letter to complete the registration'

    def test_upload_notification_list_empty_file(self, authenticated_client):
        authenticated_client.user.is_staff = True
        authenticated_client.user.save()
        file = SimpleUploadedFile(
            name='notification_list.xlsx',
            content=None,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response = authenticated_client.post(reverse('notificationlist'), data={'file': file}, format='multipart')
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['file'] == ['The submitted file is empty.']

    def test_upload_notification_list_invalid_main_key(self, authenticated_client):
        authenticated_client.user.is_staff = True
        authenticated_client.user.save()
        file_path = str(settings.BASE_DIR) + r'\notification_center\tests\notification_list_invalid_1.xlsx'
        file = SimpleUploadedFile(
            name='notification_list.xlsx',
            content=open(file_path, 'rb').read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response = authenticated_client.post(reverse('notificationlist'), data={'file': file}, format='multipart')
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json == ['Upload file according to the terms of use']

    def test_upload_notification_list_invalid_value_key(self, authenticated_client):
        authenticated_client.user.is_staff = True
        authenticated_client.user.save()
        file_path = str(settings.BASE_DIR) + r'\notification_center\tests\notification_list_invalid_2.xlsx'
        file = SimpleUploadedFile(
            name='notification_list.xlsx',
            content=open(file_path, 'rb').read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response = authenticated_client.post(reverse('notificationlist'), data={'file': file}, format='multipart')
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json == ['Upload file according to the terms of use']
