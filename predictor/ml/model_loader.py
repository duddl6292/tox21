import json
from pathlib import Path

import joblib
from tensorflow.keras.models import load_model


BASE_DIR = Path(__file__).resolve().parent


# FFNN 모델 로딩
# compile=False를 쓰면 custom loss나 optimizer 때문에 로딩 실패하는 일을 줄일 수 있음
NR_ER_MODEL = load_model(
    BASE_DIR / "NR_ER_ffnn.keras",
    compile=False
)

SR_P53_MODEL = load_model(
    BASE_DIR / "SR_p53_ffnn.keras",
    compile=False
)


# feature 설정 로딩
with open(BASE_DIR / "feature_config.json", "r", encoding="utf-8") as f:
    FEATURE_CONFIG = json.load(f)


FEATURE_COLUMNS = joblib.load(BASE_DIR / "feature_columns.pkl")
DESCRIPTOR_COLUMNS = joblib.load(BASE_DIR / "descriptor_columns.pkl")
BIT_COLUMNS = joblib.load(BASE_DIR / "bit_columns.pkl")


# threshold
NR_ER_THRESHOLD = FEATURE_CONFIG["thresholds"]["nr_er"]
SR_P53_THRESHOLD = FEATURE_CONFIG["thresholds"]["sr_p53"]


# risk bin
LOW_RISK_CUTOFF = FEATURE_CONFIG["risk_bins"]["low"]
HIGH_RISK_CUTOFF = FEATURE_CONFIG["risk_bins"]["high"]