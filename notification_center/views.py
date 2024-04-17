from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from notification_center.serializers import NotificationSerializer


class NotificationUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = (MultiPartParser,)
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'upload': 'You have successfully updated the list of notifications.'},
                        status=status.HTTP_200_OK)
