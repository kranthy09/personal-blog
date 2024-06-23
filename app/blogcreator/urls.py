"""
URL mappings for the Blog app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blogcreator import views

router = DefaultRouter()
router.register("blogs", views.BlogViewSet)

app_name = "blogcreator"


urlpatterns = [
    path("", include(router.urls)),
]
