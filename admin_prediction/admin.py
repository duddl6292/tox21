from django.contrib import admin
from .models import PredictionJob, PredictionResult


@admin.register(PredictionJob)
class PredictionJobAdmin(admin.ModelAdmin):

    # ==========================================================
    # 관리자 목록 화면에 표시할 컬럼
    # ==========================================================
    list_display = (
        "id",
        "user",
        "file_name",      # 업로드한 CSV 파일명
        "total_count",    # 전체 분석 개수
        "success_count",  # 성공 개수
        "error_count",    # 실패 개수
        "created_at",     # 분석 시간
    )
    
    # ==========================================================
    # 파일명 검색 기능
    # ==========================================================
    search_fields = (
        "file_name",
        "user__username",
    )

    list_filter = (
        "created_at",
        "user",
    )
    # ==========================================================
    # 최신 분석 결과가 위에 오도록 정렬
    # ==========================================================
    ordering = (
        "-created_at",
    )

    # ==========================================================
    # 읽기 전용
    # 사용자가 수정하지 못하도록 설정
    # ==========================================================
    readonly_fields = (
        "file_name",
        "user",
        "total_count",
        "success_count",
        "error_count",
        "created_at",
    )
    # ==========================================================
    # "ML 예측 추가" 버튼 제거
    # CSV 업로드 시 자동 생성되므로 직접 추가할 필요 없음
    # ==========================================================
    def has_add_permission(self, request):
        return False

    # ==========================================================
    # 수정 금지
    # 예측 결과는 시스템이 자동 생성하므로 수정 불가
    # ==========================================================
    def has_change_permission(self, request, obj=None):
        return False
    
@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "id",
        "job",
        "row_number",
        "resolved_name",
        "nr_er_source",
        "nr_er_result",
        "nr_er_risk",
        "sr_p53_source",
        "sr_p53_result",
        "sr_p53_risk",
    )

    search_fields = (
        "input_name",
        "resolved_name",
        "input_smiles",
        "canonical_smiles",
    )

    list_filter = (
        "nr_er_source",
        "nr_er_risk",
        "sr_p53_source",
        "sr_p53_risk",
    )

    ordering = (
        "-id",
    )

    readonly_fields = (
        "job",
        "row_number",
        "input_name",
        "input_smiles",
        "resolved_name",
        "canonical_smiles",
        "nr_er_source",
        "nr_er_result",
        "nr_er_prob",
        "nr_er_risk",
        "sr_p53_source",
        "sr_p53_result",
        "sr_p53_prob",
        "sr_p53_risk",
        "message",
    )

    # ==========================================================
    # "ML 예측 추가" 버튼 제거
    # CSV 업로드 시 자동 생성되므로 직접 추가할 필요 없음
    # ==========================================================
    def has_add_permission(self, request):
        return False

    # ==========================================================
    # 수정 금지
    # 예측 결과는 시스템이 자동 생성하므로 수정 불가
    # ==========================================================
    def has_change_permission(self, request, obj=None):
        return False

