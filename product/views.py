from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from Web_Menu_DA.permissions import IsOwnerOr404
from product.business_logic import deny_duplicates_save
from product.models import Product, Category
from product.serializers import ProductSerializer, CreateProductSerializer, CreateCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOr404]    #todo add permission IsManagerOr404
    serializer_class = ProductSerializer

    def get_queryset(self):
        """Custom permission type of IsOwnerOr404.
        queryset = Product.objects.all() this one take all products
        and next one only owners products that filter through the company"""
        # todo add filter by location
        return Product.objects.filter(company__owner_id=self.request.user.id).order_by('id')
        # .order_by('id') to improve UnorderedObjectListWarning: Pagination may yield inconsistent results with
        # an unordered object_list


class CreateProductView(viewsets.ModelViewSet):
    serializer_class = CreateProductSerializer
    permission_classes = [IsAuthenticated, IsOwnerOr404]    #todo add permission IsManagerOr404

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {})  # if no dict in kwargs we make it
        # join user to the serializer context for opportunity def validate in CreateCompanySerializer
        kwargs['context']['user'] = self.request.user
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        # todo add filter by location
        return Product.objects.filter(company__owner_id=self.request.user.id).order_by('id')


class CreateCategoryView(viewsets.ModelViewSet):
    serializer_class = CreateCategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOr404]    #todo add permission IsManagerOr404

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {})  # if no dict in kwargs we make it
        # join user to the serializer context for opportunity def validate in CreateCompanySerializer
        # We need to add category == obj to 'context'
        if category := self.kwargs.get('pk', None):
            try:
                category = self.get_object()
            except Http404:
                category = None
        kwargs['context']['user'] = self.request.user
        kwargs['context']['category'] = category
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        return Category.objects.filter(location__company__owner_id=self.request.user.id).order_by('id')

    def perform_create(self, serializer):
        root_category = serializer.validated_data['name']
        child_category = serializer.validated_data.pop('child_category', None)
        with transaction.atomic():
            try:
                deny_duplicates_save(root_category)
                root = Category.add_root(name=root_category)
                root.location.set([serializer.validated_data['location']])
                if child_category:
                    node = root.add_child(name=child_category)
                    node.location.set([serializer.validated_data['location']])
            except ValidationError as error:
                if not child_category:
                    raise error
                deny_duplicates_save(child_category)
                root = Category.objects.get(name=root_category)
                node = root.add_child(name=child_category)
                node.location.set([serializer.validated_data['location']])

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        try:
            category = self.get_object()
            new_root = serializer.validated_data.get('new_root', None)
            try:
                deny_duplicates_save(serializer.validated_data['name'])
                category.name = serializer.validated_data['name']
                category.save()
            except ValidationError as error:
                if category.get_root() == new_root or not new_root:
                    raise error
            if serializer.validated_data['location']:
                category.location.clear()
                category.location.set([serializer.validated_data['location']])
            if not category.is_root() and new_root:
                category.move(new_root, pos='first-child')
        except ObjectDoesNotExist:
            raise Http404
