
from django.db import models


# ==========================================================
# 공지사항 모델
# 관리자 페이지에서 공지사항을 관리하기 위한 모델
# ==========================================================

class Notice(models.Model):

    # 공지 제목
    title = models.CharField(
        max_length=200,
        verbose_name="공지 제목"
    )

    # 공지 내용
    content = models.TextField(
        verbose_name="공지 내용"
    )

    # 작성일
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="작성일"
    )

    # 수정일
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일"
    )

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항 관리"

    def __str__(self):
        return self.title

