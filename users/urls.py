from django.urls import path
from .views import ProfileInfoView

urlpatterns = [
    path("profile/<uuid:user_id>/", ProfileInfoView.as_view(), name="get_profile_info"),
]
