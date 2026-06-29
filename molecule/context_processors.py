from django.contrib.auth.models import User


def dashboard_counts(request):
    # 회원 수
    user_count = User.objects.count()

    # Tox21 화합물 수
    try:
        from predictor.models import Molecule
        chemical_count = Molecule.objects.count()
    except Exception:
        chemical_count = 0

    # CSV 업로드 / 분석 작업 수
    try:
        from predictor.models import AnalysisJob
        csv_count = AnalysisJob.objects.count()
    except Exception:
        csv_count = 0

    # ML 예측 결과 수
    try:
        from predictor.models import AnalysisResult
        predict_count = AnalysisResult.objects.count()
    except Exception:
        predict_count = 0

    return {
        "user_count": user_count,
        "chemical_count": chemical_count,
        "csv_count": csv_count,
        "predict_count": predict_count,
    }