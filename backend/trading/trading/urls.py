
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),  # Регистрация, выход и т.д.
    path('auth/', include('djoser.urls.jwt')),  # JWT-токены
    path('api/', include('trading_app.api.urls')),
]
