from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisaTypeViewSet, ApplicationViewSet

router = DefaultRouter()
router.register(r'visas', VisaTypeViewSet, basename='visa')
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
]
