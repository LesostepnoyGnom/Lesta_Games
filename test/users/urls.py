from django.urls import path
from . import views
from .views import delete_account, change_password

app_name = "users"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register, name="register"),
    path('delete-account/', delete_account, name='delete_account'),
    path('change_password/', change_password, name='change_password'),
]
