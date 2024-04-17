from django.urls import path

from notification_center.views import NotificationUploadView

urlpatterns = [
    path('upload/notificationlist/', NotificationUploadView.as_view(), name='notificationlist'),
]
