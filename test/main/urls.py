
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('test_page', views.test_pg)
]
