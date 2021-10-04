from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # User management
    path('accounts/', include('allauth.urls')),

    # Local apps
    path('', include('pages.urls', namespace='pages')),
    path('leagues/', include('leagues.urls', namespace='leagues')),
    path('simulation/', include('simulation.urls', namespace='simulation')),
]