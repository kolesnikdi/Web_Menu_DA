from django.db import models
from django.utils import timezone

from treebeard.mp_tree import MP_Node

from Web_Menu_DA.constants import Measures


class Product(models.Model):
    company = models.ForeignKey('company.Company', related_name='company', on_delete=models.CASCADE)
    locations = models.ManyToManyField('location.Location', related_name='product_location')
    name = models.CharField('name', max_length=15)
    description = models.CharField('description', max_length=30)
    volume = models.PositiveSmallIntegerField('volume', default=0)
    # choices=list((i.value, i.name) for i in Measures) if 'class Measures(IntEnum)' in Web_Menu_DA.constant
    measure = models.PositiveSmallIntegerField('measure', choices=Measures.choices)
    cost = models.DecimalField('cost', decimal_places=2, default=0, max_digits=7)
    logo = models.OneToOneField('image.Image', related_name='product_logo', null=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    category = models.ManyToManyField('product.Category', related_name='category')

    def __str__(self):
        return self.name


class Category(MP_Node):
    name = models.CharField(max_length=40)
    location = models.ManyToManyField('location.Location', related_name='categories')

    node_order_by = None
