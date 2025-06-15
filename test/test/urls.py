from django.conf.urls import handler404
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

from main.API import (MainAPIView, MainAPIViewVersion, MainAPIViewMetrics,
                        MainAPIViewDocuments, MainAPIViewDocumentsID, MainAPIViewDocumentDelete,
                        MainAPIViewCollection, MainAPIViewCollectionID, MainAPIViewChangeCollection,
                        MainAPIViewDelCollection, MainAPIViewCollectionStat, MainAPIViewDocumentStat,
                        MainAPIViewLogout, MainAPIViewLogin, MainAPIViewRegister,
                        MainAPIViewUser, MainAPIViewUserDelete)
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

    path('api/v1/documents/', MainAPIViewDocuments.as_view()),
    path('api/v1/documents/<int:doc_id>/', MainAPIViewDocumentsID.as_view()),
    path('api/v1/documents/<int:doc_id>/statistics', MainAPIViewDocumentStat.as_view()),
    path('api/v1/documents/<int:doc_id>', MainAPIViewDocumentDelete.as_view()),

    path('api/v1/collections/', MainAPIViewCollection.as_view()),
    path('api/v1/collections/<int:coll_id>', MainAPIViewCollectionID.as_view()),
    path('api/v1/collection/<int:coll_id>/<int:doc_id>', MainAPIViewChangeCollection.as_view()),
    path('api/v1/collection/<int:doc_id>', MainAPIViewDelCollection.as_view()),
    path('api/v1/collection/<int:coll_id>/statistics', MainAPIViewCollectionStat.as_view()),

    path('api/v1/login/<str:user_login>/<str:user_password>', MainAPIViewLogin.as_view()),
    path('api/v1/logout', MainAPIViewLogout.as_view()),
    path('api/v1/register/<str:user_login>/<str:user_password>', MainAPIViewRegister.as_view()),
    path('api/v1/user/<str:user_password>/<str:new_user_password>', MainAPIViewUser.as_view()),
    path('api/v1/user/<str:user_password>', MainAPIViewUserDelete.as_view()),




    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
