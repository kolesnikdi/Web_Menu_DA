from rest_framework import serializers, exceptions
from django.db import transaction

from location.models import Location
from product.models import Product, Category
from company.models import Company
from image.models import Image
from product.business_logic import validate_image_size


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'company', 'locations', 'name', 'description', 'volume', 'measure', 'cost', 'logo']


class ProductImageSerializer(serializers.ModelSerializer):
    """Special Serializer to customize validators=[validate_image_size]"""
    image = serializers.ImageField(use_url=True, allow_null=True, validators=[validate_image_size])

    class Meta:
        model = Image
        fields = ['image']


class CreateProductSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    locations = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=True, many=True)
    logo = ProductImageSerializer(allow_null=True, required=False)

    def validate_company(self, company):  # todo when manager.exist make validator - if location not in user
        if user := self.context.get('user'):
            if company not in user.company.all():
                raise exceptions.NotFound({"company": "Company does not found."})
        return company

    def validate_locations(self, locations):
        if company_id := self.initial_data.get('company'):
            for location in locations:
                if location.company_id != int(company_id):
                    raise exceptions.NotFound({"object": "Location or/and Company does not found."})
        return locations

    class Meta:
        model = Product
        fields = ['id', 'company', 'locations', 'name', 'description', 'volume', 'measure', 'cost', 'logo']

    def create(self, validated_data):
        logo_dict = validated_data.pop('logo', None)  # for correct work we must set default None if no image in logo
        locations_list = validated_data.pop('locations')
        with transaction.atomic():
            # atomic should stop other requests to db until we make the changes
            product = Product.objects.create(
                logo=Image.objects.create(image=None),  # need to create empty logo to set company_id
                **validated_data,
            )
            # product.logo.image.save don't work if logo/image None so we need we have to rule out these options
            if logo_dict and logo_dict.get('image'):
                product.logo.image.save(f'{product.name}.jpg', logo_dict['image'])
            product.locations.set(locations_list)
        return product

    def update(self, instance, validated_data):
        logo_dict = validated_data.pop('logo')
        # make logo object separately by using custom 'Serializer'
        if logo_dict and logo_dict.get('image'):
            instance.logo.image.delete()
            instance.logo.image.save(f'{instance.name}.jpg', logo_dict['image'])
        else:
            instance.logo = ProductImageSerializer().update(instance.logo, logo_dict)
        return super().update(instance, validated_data)  # using default method - 'update' for company


class CreateCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=40)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        if user := kwargs.get("context").get("user", None):
            """It is the way to make filter() and return that queries that depends to the user only"""
            self.fields['location'].queryset = Location.objects.filter(company__owner=user)
            # self.fields['child_category'] = serializers.CharField(write_only=True, max_length=40)
        if category := kwargs.get("context").get('category', None):  # for def perform_update()
            """delete and add new field if our request is PUT PUTCH DELETE"""
            del self.fields['child_category']
            if not category.is_root():
                self.fields['new_root'] = serializers.PrimaryKeyRelatedField(queryset=Category.objects.none(),
                                                                             required=True, write_only=True)
                self.fields['new_root'].queryset = Category.objects.filter(location__in=category.location.all(),
                                                                           depth=1)
        super().__init__(*args, **kwargs)

    """ get_fields() or enable 83 str
    write_only=True don't help with  ModelViewSet so we need this function to add
     child_category field that not depends to the Category """

    def get_fields(self):
        fields = super().get_fields()
        fields['child_category'] = serializers.CharField(write_only=True, max_length=40, required=False)
        return fields

    def validate_location(self, location):
        if user := self.context.get('user'):
            company_qr = user.company.all()
            if all(location not in company.location.all() for company in company_qr):
                raise exceptions.NotFound({"location": "Location does not found."})
        return location

    """It allows us to left only one instance for input in location field and don't use many=True.
    And in the same time we represent full data of location as ManyToMany logic is"""

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(instance, Category):  # for def perform_update
            representation['location'] = [{'id': location.id} for location in
                                          Category.objects.get(id=instance.id).location.all()]
            representation['child_nodes'] = [{'id': children.id} for children in
                                             Category.objects.get(id=instance.id).get_children()]
        else:
            if name := representation.get('name', None):  # def perform_create
                representation['location'] = [{'id': location.id} for location in
                                              Category.objects.get(name=name).location.all()]
                representation['child_nodes'] = [{'id': children.id} for children in
                                                 Category.objects.get(name=name).get_children()]
        return representation

    class Meta:
        model = Category
        fields = ['id', 'name', 'location']
