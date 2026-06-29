from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import TemplateView


admin.site.site_header = "Tox21 관리자 페이지"
admin.site.site_title = "Tox21 Admin"
admin.site.index_title = "Tox21 데이터 관리"


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("chemicals/", include("chemicals.urls")),
    path("predictor/", include("predictor.urls")), # predictor.urls추가
    path("chemical-news/", views.chemical_news, name="chemical_news"),
    path("privacy/", TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
    path("kpis/<str:page>/", views.kpis_view, name="kpis_view"),
    path("editor/", include("editor.urls")), # editor 추가
    path("prediction/", include("prediction.urls")),
    path(
    "introduce/",
    TemplateView.as_view(template_name="introduce/about.html"),
    name="introduce"),
]