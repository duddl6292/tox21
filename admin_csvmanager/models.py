from django.db import models


class CSVUpload(models.Model):
    """
    업로드한 CSV 파일의 정보를 저장하는 모델
    (업로드 이력 관리용)
    """

    # 업로드한 CSV 파일
    file = models.FileField(
        "CSV 파일",
        upload_to="csv/"
    )

    # 업로드 시간
    uploaded_at = models.DateTimeField(
        "업로드일",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "CSV 업로드"
        verbose_name_plural = "CSV 업로드"

    def __str__(self):
        return self.file.name