from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("mypage/", views.mypage, name="mypage"),
    path("delete/", views.user_delete, name="user_delete"),
    path('delete/', views.delete_account, name='delete_account'),


    path("admin/users/", views.admin_user_list, name="admin_user_list"),
    path("admin/users/<int:pk>/", views.admin_user_detail, name="admin_user_detail"),
    path("admin/users/<int:pk>/edit/", views.admin_user_update, name="admin_user_update"),
    path("admin/users/<int:pk>/password/", views.admin_password_reset, name="admin_password_reset"),
    path("admin/users/<int:pk>/delete/", views.admin_user_delete, name="admin_user_delete"),
]