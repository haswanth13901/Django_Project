from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def home_view(request):
    return JsonResponse({
        "message": "Welcome to the Doctor Finder API",
        "available_endpoints": [
            "/admin/",
            "/api/",
            "/api/token/",
            "/api/token/refresh/"
        ]
    })

urlpatterns = [
    path('', home_view),  
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('fhirapi.urls')),
]
