from datetime import datetime
import pytest

from django.urls import reverse
from django.core.cache import cache
from knox.models import AuthToken

from rest_framework import status, exceptions

from Web_Menu_DA.constants import CredentialsChoices
from registration.business_logic import final_creation
from registration.models import RegistrationTry, WebMenuUser, BanHistory, LoginHistory
from registration.serializers import CreateRegisterTrySerializer, RegisterConfirmSerializer, WebMenuUserSerializer


class TestValidatePassword:

    def test_passwords_equal(self, randomizer):
        validated_data = randomizer.upp2_data()
        attrs = {
            'password': validated_data,
            'password2': validated_data,
        }

        result = RegisterConfirmSerializer.validate(None, attrs)
        assert result['password'] == result['password2']

    def test_passwords_different(self, randomizer):
        attrs = {
            'password': randomizer.upp2_data(),
            'password2': randomizer.upp2_data(),
        }
        # check that exception rise
        with pytest.raises(exceptions.ValidationError) as exc:
            RegisterConfirmSerializer.validate(None, attrs)
        assert "Password fields didn't match." in str(exc.value)
        assert exc.type == exceptions.ValidationError


class TestBusinessLogic:

    @pytest.mark.django_db
    def test_final_creation(self, randomizer):
        validated_data = randomizer.user()
        reg_try = RegistrationTry.objects.create(email=randomizer.email())
        result = final_creation(validated_data, reg_try)
        assert isinstance(result, WebMenuUser)
        assert result.first_name == validated_data['first_name']
        assert result.last_name == validated_data['last_name']
        assert result.email == reg_try.email
        assert result.mobile_phone == validated_data['mobile_phone']
        assert result.fathers_name == validated_data['fathers_name']
        assert result.country == validated_data['country']
        assert result.city == validated_data['city']
        assert result.street == validated_data['street']
        assert result.house_number == validated_data['house_number']
        assert result.flat_number == validated_data['flat_number']
        assert result.passport_series == validated_data['passport_series']
        assert result.passport_number == validated_data['passport_number']
        assert result.passport_date_of_issue == validated_data['passport_date_of_issue']
        assert result.passport_issuing_authority == validated_data['passport_issuing_authority']
        for_check_reg_try = RegistrationTry.objects.filter(id=reg_try.id).first()
        assert for_check_reg_try.confirmation_time is not None


class TestApiClientView:

    @pytest.mark.django_db
    def test_registration_valid_data(self, api_client, randomizer):
        response = api_client.post(reverse('user_reg'), data={'email': randomizer.email()}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()  # check that response is not empty
        assert set(response.json().keys()) == set(CreateRegisterTrySerializer.Meta.fields)
        assert response.json()['email'] == response.data['email']

    @pytest.mark.django_db
    def test_registration_null_data(self, api_client):
        response = api_client.post(reverse('user_reg'), data={'email': None}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()

    @pytest.mark.django_db
    def test_full_registration_valid_data(self, api_client, reg_try, randomizer):
        validated_data = randomizer.user()
        data = {'password': validated_data['password'],
                'password2': validated_data['password'],
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'fathers_name': validated_data['fathers_name'],
                'mobile_phone': validated_data['mobile_phone'],
                'country': validated_data['country'],
                'city': validated_data['city'],
                'street': validated_data['street'],
                'house_number': validated_data['house_number'],
                'flat_number': validated_data['flat_number'],
                'passport_series': validated_data['passport_series'],
                'passport_number': validated_data['passport_number'],
                'passport_date_of_issue': validated_data['passport_date_of_issue'],
                'passport_issuing_authority': validated_data['passport_issuing_authority'],
                }
        data_reg_try = RegistrationTry.objects.get(email=reg_try.data['email'])
        url = reverse('registration_confirm', args=[data_reg_try.code])
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()
        assert set(response.json().keys()) >= set(WebMenuUserSerializer.Meta.fields)
        assert response.json()['email'] == reg_try.data['email']
        for_check_reg_try = RegistrationTry.objects.get(id=data_reg_try.id)
        assert for_check_reg_try.confirmation_time is not None
        for_check_user = WebMenuUser.objects.get(email=reg_try.data['email'])
        assert for_check_user.first_name == validated_data['first_name']
        assert for_check_user.last_name == validated_data['last_name']
        assert for_check_user.mobile_phone == validated_data['mobile_phone']
        assert for_check_user.fathers_name == validated_data['fathers_name']
        assert for_check_user.country == validated_data['country']
        assert for_check_user.city == validated_data['city']
        assert for_check_user.street == validated_data['street']
        assert for_check_user.house_number == validated_data['house_number']
        assert for_check_user.flat_number == validated_data['flat_number']
        assert for_check_user.passport_series == validated_data['passport_series']
        assert for_check_user.passport_number == validated_data['passport_number']
        assert for_check_user.passport_date_of_issue == validated_data['passport_date_of_issue']
        assert for_check_user.passport_issuing_authority == validated_data['passport_issuing_authority']

    @pytest.mark.django_db
    def test_full_registration_reg_done_code(self, api_client, randomizer, reg_done_code):
        validated_data = randomizer.user()
        url = reverse('registration_confirm', args=[reg_done_code])
        validated_data.update({'password2': validated_data['password']})
        response = api_client.post(url, data=validated_data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()
        assert response.json()['detail'] == 'Not found.'

    @pytest.mark.django_db
    def test_full_registration_invalid_code(self, api_client, randomizer):
        validated_data = randomizer.user()
        url = reverse('registration_confirm', args=['902999ff-37d7-4125-bd84-5aaf24f1f14a'])
        validated_data.update({'password2': validated_data['password']})
        response = api_client.post(url, data=validated_data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()
        assert response.json()['detail'] == 'Not found.'


class TestKnoxView:
    @pytest.mark.django_db
    def test_login_valid_data(self, api_client, user):
        AuthToken.objects.filter(user_id=user.id).delete()  # delete from db all tokens for user
        response = api_client.post(reverse('login'),
                                   data={
                                       'username': user.email,
                                       'password': user.user_password,
                                   }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        resp_json = response.json()
        assert resp_json
        assert set(resp_json['user']) >= set(WebMenuUserSerializer.Meta.fields)
        assert resp_json['token'] is not None
        assert resp_json['expiry'] is not None
        assert AuthToken.objects.filter(user_id=user.id).exists()
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {resp_json["token"]}')
        response2 = api_client.get(reverse('user'), format='json')
        assert response2.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_login_invalid_data(self, api_client, randomizer):
        response = api_client.post(reverse('login'),
                                   data={
                                       'username': randomizer.upp2_data(),
                                       'password': randomizer.upp2_data(),
                                   }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()
        assert response.json()['non_field_errors'] == ['Access denied: wrong username or password.']

    @pytest.mark.django_db
    def test_logout(self, authenticated_client):
        response = authenticated_client.post(reverse('logout'), format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not AuthToken.objects.filter(user_id=authenticated_client.user.id).exists()
        response = authenticated_client.get(reverse('user'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_logoutall(self, authenticated_client_2):
        response = authenticated_client_2.post(reverse('logoutall'), format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not AuthToken.objects.filter(user_id=authenticated_client_2.user.id).exists()
        response = authenticated_client_2.get(reverse('user'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDjangoRegistrationFormFunction:

    @pytest.mark.django_db
    def test_registration_form_valid_data(self, api_client, randomizer):
        response = api_client.post(reverse('djangoform'), data={'email': randomizer.email()})
        assert response.status_code == status.HTTP_302_FOUND

    @pytest.mark.django_db
    def test_registration_funcrion_valid_data(self, api_client, randomizer):
        response = api_client.post(reverse('djangofunction'), data={'email': randomizer.email()})
        assert 'The Email was send successfully' in response.content.decode('utf-8')
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_full_registration_funcrion_valid_data(self, api_client, reg_try, randomizer):
        validated_data = randomizer.user()
        data = {'password': validated_data['password'],
                'confirm_password': validated_data['password'],
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'fathers_name': validated_data['fathers_name'],
                'mobile_phone': validated_data['mobile_phone'],
                'country': validated_data['country'],
                'city': validated_data['city'],
                'street': validated_data['street'],
                'house_number': validated_data['house_number'],
                'flat_number': validated_data['flat_number'],
                'passport_series': validated_data['passport_series'],
                'passport_number': validated_data['passport_number'],
                'passport_date_of_issue': validated_data['passport_date_of_issue'],
                'passport_issuing_authority': validated_data['passport_issuing_authority'],
                }
        data_reg_try = RegistrationTry.objects.get(email=reg_try.data['email'])
        url = reverse('djangofunction_confirm', args=[data_reg_try.code])
        response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'You create user successful.' in response.content.decode('utf-8')
        for_check_user = WebMenuUser.objects.get(email=reg_try.data['email'])
        assert for_check_user.first_name == validated_data['first_name']
        assert for_check_user.last_name == validated_data['last_name']
        assert for_check_user.mobile_phone == validated_data['mobile_phone']
        assert for_check_user.fathers_name == validated_data['fathers_name']
        assert for_check_user.country == validated_data['country']
        assert for_check_user.city == validated_data['city']
        assert for_check_user.street == validated_data['street']
        assert for_check_user.house_number == validated_data['house_number']
        assert for_check_user.flat_number == validated_data['flat_number']
        assert for_check_user.passport_series == validated_data['passport_series']
        assert for_check_user.passport_number == validated_data['passport_number']
        assert for_check_user.passport_date_of_issue == validated_data['passport_date_of_issue']
        assert for_check_user.passport_issuing_authority == validated_data['passport_issuing_authority']
        for_check_reg_try = RegistrationTry.objects.get(id=data_reg_try.id)
        assert for_check_reg_try.confirmation_time is not None


class TestRequestTracker:

    @pytest.mark.django_db
    def test_invalid_login_data_2min_ban(self, api_client, randomizer):
        time = CredentialsChoices.login.intervals[1] / 60
        tries = 4
        for trie in range(tries):
            response = api_client.post(reverse('login'),
                                       data={
                                           'username': randomizer.upp2_data(),
                                           'password': randomizer.upp2_data(),
                                       }, format='json')
        response_json = response.json()
        delete_cache = cache.delete('127.0.0.1_Other / Other / Other')
        assert delete_cache is True
        assert response_json
        assert response_json['non_field_errors'][0] == f'To many tries. Opportunity is blocked for {time} minutes'
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data_for_check = BanHistory.objects.filter(ip_address='127.0.0.1', user_agent='Other / Other / Other').last()
        assert data_for_check.credentials_interval == 120
        data_for_check.delete()

    @pytest.mark.django_db
    def test_invalid_login_data_set_to_total_ban(self, api_client, randomizer):
        setups = CredentialsChoices.login
        instance = BanHistory(
            account=None,
            ip_address='127.0.0.1',
            user_agent='Other / Other / Other',
            **dict(zip(setups.fields, [setups.intervals[-2], datetime(2024, 4, 16, 8, 32, 32, 784484)])),
        )
        instance.save()
        tries = 3
        for trie in range(tries):
            response = api_client.post(reverse('login'),
                                       data={
                                           'username': randomizer.upp2_data(),
                                           'password': randomizer.upp2_data(),
                                       }, format='json')
        response_json = response.json()
        delete_cache = cache.delete('127.0.0.1_Other / Other / Other')
        assert delete_cache is True
        assert response_json
        assert response_json['non_field_errors'][0] == 'To many tries. You are blocked'
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data_for_check_b = BanHistory.objects.filter(ip_address='127.0.0.1', user_agent='Other / Other / Other').last()
        assert data_for_check_b.credentials_interval == 0
        data_for_check_b.delete()
        data_for_check = LoginHistory.objects.filter(ip_address='127.0.0.1', user_agent='Other / Other / Other').last()
        assert data_for_check.reason_of_reject == 'BAN_credentials'
        assert data_for_check.result is False
        data_for_check.delete()

    @pytest.mark.django_db
    def test_forgot_passwor_check_total_ban(self, api_client, randomizer):
        setups = CredentialsChoices.login
        instance = BanHistory(
            account=None,
            ip_address='127.0.0.1',
            user_agent='Other / Other / Other',
            ban_time=datetime(2024, 4, 16, 8, 32, 32, 784484),
            **dict(zip(setups.fields, [setups.intervals[-1], datetime(2024, 4, 16, 8, 32, 32, 784484)])),
        )
        instance.save()
        response = api_client.post(reverse('login'),
                                   data={
                                       'username': randomizer.upp2_data(),
                                       'password': randomizer.upp2_data(),
                                   }, format='json')
        response_json = response.json()
        assert response_json
        assert response_json['non_field_errors'][0] == 'To many tries. You are blocked'
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data_for_check = BanHistory.objects.filter(ip_address='127.0.0.1', user_agent='Other / Other / Other').last()
        assert data_for_check.credentials_interval == 0
        data_for_check.delete()
