from django.urls import reverse
from rest_framework import status

from product.models import Category


class TestCreateCategoryView:
    def test_create_category_valid(self, custom_location, randomizer):
        data = {'name': 'name', 'location': custom_location.id, 'child_category': 'child_category'}
        response = custom_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_201_CREATED
        data_for_check_root = Category.objects.get(name='name')
        assert data_for_check_root.name == response_json['name']
        assert data_for_check_root.location.last().id == response_json['location'][0]['id']
        data_for_check_child = Category.objects.get(name='child_category')
        assert data_for_check_child.id == response_json['child_nodes'][0]['id']

    def test_create_new_child_valid(self, custom_category):
        data = {'name': custom_category.name, 'location': custom_category.c_location.id, 'child_category': 'child'}
        response = custom_category.c_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_201_CREATED
        data_for_check_root = Category.objects.get(name=data['name'])
        assert data['child_category'] in [name.name for name in data_for_check_root.get_children()]

    def test_create_empty_root_valid(self, custom_location):
        data = {'location': custom_location.id, 'child_category': 'child_category'}
        response = custom_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['name'] == ['This field is required.']

    def test_create_empty_child_valid(self, custom_location):
        data = {'name': 'name', 'location': custom_location.id}
        response = custom_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_201_CREATED
        data_for_check_root = Category.objects.get(name='name')
        assert data_for_check_root.name == response_json['name']
        assert data_for_check_root.location.last().id == response_json['location'][0]['id']
        assert not data_for_check_root.get_children().exists()

    def test_create_empty_location_valid(self, custom_location):
        data = {'name': 'name', 'child_category': 'child_category'}
        response = custom_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['location'] == ['This field is required.']

    def test_create_duplicate_child(self, custom_category):
        data = {'name': custom_category.name,
                'location': custom_category.c_location.id,
                'child_category': 'child_category'}
        response = custom_category.c_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['error'] == 'Category with the same name already exists at this level.'

    def test_create_duplicate_root(self, custom_category):
        data = {'name': custom_category.name,
                'location': custom_category.c_location.id}
        response = custom_category.c_location.user.post(reverse('category_new-list'), data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['error'] == 'Category with the same name already exists at this level.'

    def test_update_maine_category_valid(self, randomizer, custom_category):
        data = {'name': randomizer.random_name(), 'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_200_OK
        data_for_check_root = Category.objects.get(id=custom_category.id)
        assert data_for_check_root.name == data['name']

    def test_update_maine_category_duplicate_root(self, randomizer, custom_category):
        data = {'name': custom_category.name, 'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['error'] == 'Category with the same name already exists at this level.'

    def test_update_empty_root(self, randomizer, custom_category):
        data = {'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['name'] == ['This field is required.']

    def test_update_root_empty_location(self, randomizer, custom_category):
        data = {'name': custom_category.name}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['location'] == ['This field is required.']

    def test_update_child_category_valid(self, randomizer, custom_category, custom_category_2):
        data = {'name': randomizer.random_name(),
                'location': custom_category.c_location.id,
                'new_root': custom_category_2.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_200_OK
        data_for_check_root = Category.objects.get(id=custom_category.child.id)
        assert data_for_check_root.name == data['name']
        assert data_for_check_root.get_root() == custom_category_2

    def test_update_child_category_same_root_valid(self, randomizer, custom_category):
        data = {'name': randomizer.random_name(),
                'location': custom_category.c_location.id,
                'new_root': custom_category.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_200_OK
        data_for_check_root = Category.objects.get(id=custom_category.child.id)
        assert data_for_check_root.name == data['name']
        assert data_for_check_root.get_root() == custom_category

    def test_update_child_category_duplicate(self, randomizer, custom_category):
        data = {'name': custom_category.child.name,
                'location': custom_category.c_location.id,
                'new_root': custom_category.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['error'] == 'Category with the same name already exists at this level.'

    def test_update_empty_child(self, randomizer, custom_category):
        data = {'location': custom_category.c_location.id,
                'new_root': custom_category.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['name'] == ['This field is required.']

    def test_update_child_empty_location(self, randomizer, custom_category):
        data = {'name': custom_category.child.name,
                'new_root': custom_category.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['location'] == ['This field is required.']

    def test_update_child_empty_new_root(self, randomizer, custom_category):
        data = {'name': custom_category.child.name,
                'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json['new_root'] == ['This field is required.']

    def test_deny_putch_method(self, randomizer, custom_category):
        data = {'name': randomizer.random_name(), 'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.patch(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response_json['error'] == 'Method not allowed'

    def test_update_object_does_not_exist(self, randomizer, custom_category):
        data = {'name': randomizer.random_name(), 'location': custom_category.c_location.id}
        url = reverse('category_new-detail', kwargs={'pk': 10})
        response = custom_category.c_location.user.put(url, data=data, format='json')
        response_json = response.json()
        assert response_json
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_json['detail'] == 'Not found.'

    def test_delete_root(self, randomizer, custom_category):
        url = reverse('category_new-detail', kwargs={'pk': custom_category.id})
        response = custom_category.c_location.user.delete(url, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(name=custom_category).exists()

    def test_delete_child(self, randomizer, custom_category):
        url = reverse('category_new-detail', kwargs={'pk': custom_category.child.id})
        response = custom_category.c_location.user.delete(url, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(name=custom_category.child.id).exists()



