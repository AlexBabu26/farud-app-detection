from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.apps_store.models import MobileApp
from .models import Review
from .serializers import ReviewBulkUploadSerializer, ReviewSerializer


def _get_user_app_or_404(user, app_id: int) -> MobileApp:
    try:
        app = MobileApp.objects.get(id=app_id)
    except MobileApp.DoesNotExist:
        raise NotFound("App not found.")

    if app.created_by_id != user.id:
        raise PermissionDenied("You do not have permission to access this app.")
    return app


class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD reviews. Users only access reviews for apps they own.
    Query param: ?app=<app_id>
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Review.objects.filter(app__created_by=self.request.user)
        app_id = self.request.query_params.get("app")
        if app_id:
            qs = qs.filter(app_id=app_id)
        return qs

    def perform_create(self, serializer):
        app = serializer.validated_data["app"]
        if app.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to add reviews to this app.")
        serializer.save()

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.app.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to modify this review.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.app.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to delete this review.")
        instance.delete()


class ReviewBulkUploadAPIView(APIView):
    """
    POST /api/reviews/bulk/
    Body:
    {
      "app_id": 1,
      "reviews": [
        {"text":"...", "rating":5, "author":"...", "review_date":"...", "source":"..."},
        ...
      ]
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReviewBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        app = _get_user_app_or_404(request.user, serializer.validated_data["app_id"])
        reviews_data = serializer.validated_data["reviews"]

        created = []
        for item in reviews_data:
            created.append(Review(
                app=app,
                text=item["text"],
                rating=item.get("rating"),
                author=item.get("author"),
                review_date=item.get("review_date"),
                source=item.get("source"),
            ))

        Review.objects.bulk_create(created, batch_size=500)
        return Response(
            {"created_count": len(created)},
            status=status.HTTP_201_CREATED
        )

