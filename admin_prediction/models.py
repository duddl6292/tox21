from django.db import models
from predictor.models import AnalysisJob, AnalysisResult


# ==========================================================
# 사용자 ML 예측 작업 이력
# predictor.AnalysisJob 테이블을 그대로 사용
# ==========================================================
class PredictionJob(AnalysisJob):
    class Meta:
        proxy = True
        verbose_name = "ML 예측 관리"
        verbose_name_plural = "ML 예측 관리"


# ==========================================================
# 사용자 ML 예측 상세 결과
# predictor.AnalysisResult 테이블을 그대로 사용
# ==========================================================
class PredictionResult(AnalysisResult):
    class Meta:
        proxy = True
        verbose_name = "ML 예측 결과"
        verbose_name_plural = "ML 예측 결과"

# ==========================================================
# 기존 모델
# 지금은 사용하지 않지만, 테이블 삭제 방지를 위해 남겨둠
# ==========================================================
class Prediction(models.Model):

    # 업로드한 CSV 파일명
    file_name = models.CharField(
        max_length=255,
        verbose_name="파일명"
    )

    # 전체 분석 개수
    total_count = models.PositiveIntegerField(
        default=0,
        verbose_name="전체 개수"
    )

    # 성공 개수
    success_count = models.PositiveIntegerField(
        default=0,
        verbose_name="성공"
    )

    # 실패 개수
    error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="실패"
    )

    # 분석 시간
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="분석 시간"
    )

    class Meta:
        verbose_name = "ML 예측"
        verbose_name_plural = "ML 예측 관리"

    def __str__(self):
        return self.file_name