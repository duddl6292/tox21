from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    # 검색창 화면 주소: /prediction/search/
    path('search/', views.search_engine_view, name='search'),
    
    # 시각화 화면 주소: /prediction/visualize/
    path('visualize/', views.molecule_visualize_view, name='visualize'),
    
    # 2D 이미지 다운로드 주소: /prediction/download-2d/
    path('download-2d/', views.download_2d_image, name='download_2d'),
]