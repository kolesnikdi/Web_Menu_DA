from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from registration.views import WebMenuUserViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registration.urls')),
    path('company/', include('company.urls')),
    path('location/', include('location.urls')),
    path('product/', include('product.urls')),
    path('menu/', include('menu.urls')),
    path('user/', WebMenuUserViewSet.as_view(), name='user'),
    path('enable2fa/', include('two_factor_authentication.urls')),
    path('', include('notification_center.urls')),
]

if settings.DEBUG:
    urlpatterns.append(
        re_path('^swagger/', include('swagger.urls')),
    )
