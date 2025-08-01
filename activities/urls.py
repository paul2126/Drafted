from django.urls import path
from .views import (
    ActivityListView,
    ActivityDetailView,
)

urlpatterns = [
    path("", ActivityListView.as_view(), name="activity-list"),
    path("<int:activity_id>/", ActivityDetailView.as_view(), name="activity-detail"),
]
