from django.contrib import admin
from .models import Notice


# ==========================================================
# 공지사항 관리자 페이지
# ==========================================================

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):

    # 목록에 표시할 컬럼
    list_display = (
        "title",
        "created_at",
        "updated_at",
    )

    # 검색 기능
    search_fields = (
        "title",
        "content",
    )

    # 기본 정렬
    ordering = (
        "-created_at",
    )
