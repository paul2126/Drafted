from django.urls import path
from .views import ProfileInfoView, ProfileCreateView

urlpatterns = [
    path("", ProfileCreateView.as_view(), name="make-profile"),
    path("<str:user_id>/", ProfileInfoView.as_view(), name="profile-info"),
]
