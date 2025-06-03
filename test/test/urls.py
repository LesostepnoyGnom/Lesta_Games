from django.conf.urls import handler404
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found

from main.views import MainAPIView, MainAPIViewVersion, MainAPIViewMetrics

#from main.views import page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/v1/status/', MainAPIView.as_view()),
    path('api/v1/version/', MainAPIViewVersion.as_view()),
    path('api/v1/metrics/', MainAPIViewMetrics.as_view())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
