from django.urls import path
from . import views

app_name = "chemicals"

urlpatterns = [
    path("", views.chemical_list, name="chemical_list"),
    path("new/", views.chemical_create, name="chemical_new"),
    path("<int:pk>/edit/", views.chemical_update, name="chemical_edit"),
    path("<int:pk>/delete/", views.chemical_delete, name="chemical_delete"),
    path("csv-upload/", views.chemical_csv_upload, name="chemical_csv_upload"),
]