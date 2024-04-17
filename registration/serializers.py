from rest_framework import serializers

from Web_Menu_DA.constants import CredentialsChoices
from Web_Menu_DA.custom_utils import RequestTracker
from registration.models import WebMenuUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from registration.models import RegistrationTry


class LoginWebMenuUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        else:
            check_fraud_request = RequestTracker(self.context.get('request'), CredentialsChoices.login, login=True)
            error_message = 'Access denied: wrong username or password.'
            if reject_msg := check_fraud_request.check_duplicates():
                error_message = reject_msg.get('error')
        raise serializers.ValidationError(error_message)


class WebMenuUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebMenuUser
        fields = ['id', 'email', 'mobile_phone', 'first_name', 'last_name', 'fathers_name', 'country', 'city', 'street',
                  'house_number', 'flat_number', 'passport_series', 'passport_number', 'passport_date_of_issue',
                  'passport_issuing_authority', 'system_language']


class RegisterConfirmSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = WebMenuUser
        fields = ['password', 'password2', 'first_name', 'last_name', 'fathers_name', 'mobile_phone',
                  'country', 'city', 'street', 'house_number', 'flat_number', 'passport_series', 'passport_number',
                  'passport_date_of_issue', 'passport_issuing_authority', 'system_language']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class CreateRegisterTrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationTry
        fields = ['email', ]
        extra_kwargs = {
            'email': {'required': True},
        }
