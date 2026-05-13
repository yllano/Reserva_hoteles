from django.contrib import admin
from django.urls import path, include
from users.views import direct_user_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user', direct_user_error),
    path('api/users/', include('users.urls')),
]
