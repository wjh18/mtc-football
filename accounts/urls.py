from django.urls import path
from .views import SignupPageView


urlpatterns = [
    # Override allauth.urls signup to account for CustomUser
    path('signup/', SignupPageView.as_view(), name='signup'),
]
