from django.urls import path
from . import views

app_name = "predictor"

urlpatterns = [
    path("", views.upload_csv, name="index"),
    path(
        "upload/",
        views.upload_csv,
        name="upload_csv"
    ),

    path(
        "jobs/<int:job_id>/",
        views.result_list,
        name="result_list"
    ),

    path(
        "jobs/<int:job_id>/download/",
        views.download_result_csv,
        name="download_result_csv"
    ),
    path("history/", views.history, name="history"),
    path("single/", views.single_analyze, name="single_analyze"),
    path("search/", views.search_molecule, name="search_molecule"),
    path("about/", views.about, name="about"),
        # 분자 구조 이미지
    path(
        "result-structure/<int:result_id>/",
        views.result_structure_image,
        name="result_structure_image"
    ),
    path(
        "molecule-structure/<int:molecule_id>/",
        views.molecule_structure_image,
        name="molecule_structure_image"
    ),
]

