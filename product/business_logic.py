from django.core import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework import status

from product.models import Category

VARIABLE_INT = 2
MAX_IMAGE_SIZE = VARIABLE_INT * 1024 * 1024  # if we want to use limitation in MB


def validate_image_size(image):
    size = image.size
    if size > MAX_IMAGE_SIZE:
        raise exceptions.ValidationError(f'Max file size is {str(MAX_IMAGE_SIZE)} KB')


def deny_duplicates_save(name):
    if Category.objects.filter(name=name).exists():
        raise ValidationError({'error': 'Category with the same name already exists at this level.'},
                              code=status.HTTP_400_BAD_REQUEST)
