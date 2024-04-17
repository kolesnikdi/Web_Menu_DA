from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.views import LoginView as KnoxLoginView

from Web_Menu_DA.constants import CredentialsChoices
from Web_Menu_DA.custom_utils import RequestTracker
from registration.models import RegistrationTry
from registration.serializers import RegisterConfirmSerializer, CreateRegisterTrySerializer, WebMenuUserSerializer, \
    LoginWebMenuUserSerializer
from registration.business_logic import final_send_mail, final_creation
from Web_Menu_DA.permissions import IsNotAuthenticated


class WebMenuUserViewSet(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebMenuUserSerializer

    def get_object(self):
        return self.request.user


class LoginView(KnoxLoginView):
    permission_classes = (AllowAny, IsNotAuthenticated)
    serializer_class = LoginWebMenuUserSerializer
    # authentication_classes = []    # need only if request comes with Header "Authorization"

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        request.user = user
        response = super(LoginView, self).post(request, format=None)  # turns on REST_KNOX in settings.py

        return Response(response.data, status=status.HTTP_201_CREATED)


class RegisterTryView(generics.CreateAPIView):
    serializer_class = CreateRegisterTrySerializer
    permission_classes = [IsNotAuthenticated]
    queryset = RegistrationTry.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reg_try = serializer.save()
        final_send_mail(reg_try)

        return Response(
            self.serializer_class(instance=reg_try).data,
            status=status.HTTP_201_CREATED,
        )


class RegisterConfirmView(generics.CreateAPIView):
    serializer_class = RegisterConfirmSerializer
    permission_classes = [IsNotAuthenticated]
    queryset = RegistrationTry.objects.all()
    lookup_field = 'code'

    def post(self, request, *args, **kwargs):
        try:
            reg_try = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = final_creation(serializer.validated_data, reg_try)
            response = Response(WebMenuUserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
        except RegistrationTry.DoesNotExist:
            check_fraud_request = RequestTracker(request, CredentialsChoices.registration)
            if reject_msg := check_fraud_request.check_duplicates():
                response = Response(reject_msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise Http404("No %s matches the given query." % self.queryset.model._meta.object_name)
        return response

    def get_queryset(self):
        """Check confirmation_time if it is null then allows to make registration"""
        queryset = self.queryset.filter(
            confirmation_time__isnull=True,
        )
        return queryset
