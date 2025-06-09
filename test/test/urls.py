from django.conf.urls import handler404
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

from main.views import MainAPIView, MainAPIViewVersion, MainAPIViewMetrics
from traitlets.utils.descriptions import describe

#from main.views import page_not_found

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Post API",
        default_version="1.0.0",
        description="API documentation of App"
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('users/', include('users.urls', namespace="users")),

    path('api/v1/status/', MainAPIView.as_view()),
    path('api/v1/version/', MainAPIViewVersion.as_view()),
    path('api/v1/metrics/', MainAPIViewMetrics.as_view()),

    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
