from django.urls import path
from . import views

app_name = "editor"

urlpatterns = [
    path("", views.ketcher, name="ketcher"),
    path("formula/", views.get_formula, name="get_formula"),
    path("png/", views.download_png, name="download_png"),
]