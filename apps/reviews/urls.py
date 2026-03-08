from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ReviewBulkUploadAPIView, ReviewViewSet

router = DefaultRouter()
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = [
    path("bulk/", ReviewBulkUploadAPIView.as_view(), name="review-bulk-upload"),
]
urlpatterns += router.urls

