"""
URL configuration for edusite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from edu.views import *


router1 = routers.SimpleRouter()
router1.register(r'product', ProductViewSet, basename='product')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/register/', CreateUserView.as_view()),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('api/v1/product/create/', ProductAPICreateUpdate.as_view({'post': 'create'})),
    path('api/v1/product/<int:pk>/update/', ProductAPICreateUpdate.as_view({'put': 'update'})),
    path('api/v1/', include(router1.urls)),
    #path('api/v1/product/<int:pk>/lessons/', ProductLessonView.as_view()),
    path('api/v1/product/<int:pk>/get-access/', GetAccess2.as_view()),
    path('api/v1/all-products-statistics/', ProductStatisticsList.as_view())
]
