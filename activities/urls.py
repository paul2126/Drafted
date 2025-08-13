from django.urls import path
from .views import (
    ActivityListView,
    ActivityDetailView,
    EventListView,
    EventDetailView,
)

urlpatterns = [
    path("", ActivityListView.as_view(), name="activity-list"),
    path("<int:activity_id>/", ActivityDetailView.as_view(), name="activity-detail"),
    path("<int:activity_id>/events/", EventListView.as_view(), name="event-list"),
    path("<int:activity_id>/events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
]
