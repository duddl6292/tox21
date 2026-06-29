from django.db import models
from django.contrib.auth.models import User


class ChemicalCategory(models.Model):
    name = models.CharField("카테고리명", max_length=100)
    description = models.TextField("설명", blank=True)

    def __str__(self):
        return self.name


class ToxicityEndpoint(models.Model):
    name = models.CharField("Endpoint명", max_length=100)
    description = models.TextField("설명", blank=True)
    is_active = models.BooleanField("사용 여부", default=True)

    def __str__(self):
        return self.name


class Chemical(models.Model):
    name = models.CharField("화학물질명", max_length=100)
    formula = models.CharField("화학식", max_length=100)
    smiles = models.TextField("SMILES", blank=True)
    toxicity = models.CharField("독성 결과", max_length=100, blank=True)
    description = models.TextField("설명", blank=True)
    category = models.ForeignKey(ChemicalCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="카테고리")
    endpoint = models.ForeignKey(ToxicityEndpoint, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endpoint")
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    def __str__(self):
        return self.name


class CSVUploadHistory(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="업로드 관리자")
    file_name = models.CharField("파일명", max_length=200)
    total_count = models.IntegerField("전체 데이터 수", default=0)
    success_count = models.IntegerField("성공 수", default=0)
    fail_count = models.IntegerField("실패 수", default=0)
    uploaded_at = models.DateTimeField("업로드일", auto_now_add=True)

    def __str__(self):
        return self.file_name


class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="사용자")
    smiles = models.TextField("SMILES")
    endpoint = models.ForeignKey(ToxicityEndpoint, on_delete=models.SET_NULL, null=True, blank=True)
    prediction_result = models.CharField("예측 결과", max_length=100)
    probability = models.FloatField("예측 확률", default=0)
    created_at = models.DateTimeField("예측 시간", auto_now_add=True)

    def __str__(self):
        return f"{self.smiles} - {self.prediction_result}"


class DatasetVersion(models.Model):
    version_name = models.CharField("버전명", max_length=100)
    description = models.TextField("설명", blank=True)
    is_active = models.BooleanField("현재 사용 여부", default=False)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    def __str__(self):
        return self.version_name


class Notice(models.Model):
    title = models.CharField("공지 제목", max_length=200)
    content = models.TextField("공지 내용")
    writer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="작성자")
    is_visible = models.BooleanField("노출 여부", default=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    def __str__(self):
        return self.title


class ChemicalNews(models.Model):
    title = models.CharField("뉴스 제목", max_length=200)
    source = models.CharField("출처", max_length=100, blank=True)
    link = models.URLField("뉴스 링크", blank=True)
    image_url = models.URLField("이미지 URL", blank=True)
    is_visible = models.BooleanField("노출 여부", default=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    def __str__(self):
        return self.title


class MainBanner(models.Model):
    title = models.CharField("배너 제목", max_length=200)
    subtitle = models.CharField("배너 부제목", max_length=200, blank=True)
    image_url = models.URLField("배너 이미지 URL", blank=True)
    link = models.URLField("연결 링크", blank=True)
    order = models.IntegerField("순서", default=0)
    is_active = models.BooleanField("사용 여부", default=True)

    def __str__(self):
        return self.title


class Inquiry(models.Model):
    name = models.CharField("이름", max_length=100)
    email = models.EmailField("이메일")
    title = models.CharField("문의 제목", max_length=200)
    content = models.TextField("문의 내용")
    answer = models.TextField("답변", blank=True)
    is_answered = models.BooleanField("답변 완료", default=False)
    created_at = models.DateTimeField("문의일", auto_now_add=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField("질문", max_length=200)
    answer = models.TextField("답변")
    order = models.IntegerField("순서", default=0)
    is_visible = models.BooleanField("노출 여부", default=True)

    def __str__(self):
        return self.question