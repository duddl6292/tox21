from predictor.models import Molecule

from .feature_utils import smiles_to_feature_dataframe
from .model_loader import (
    NR_ER_MODEL,
    SR_P53_MODEL,
    NR_ER_THRESHOLD,
    SR_P53_THRESHOLD,
    LOW_RISK_CUTOFF,
    HIGH_RISK_CUTOFF,
)
from .pubchem_utils import (
    get_smiles_from_pubchem_name,
    get_name_from_pubchem_smiles,
)

def get_risk_by_prob(prob):
    """
    ML 예측 확률 기준 위험도.
    """

    if prob < LOW_RISK_CUTOFF:
        return "저위험"
    elif prob < HIGH_RISK_CUTOFF:
        return "중위험"
    else:
        return "고위험"


def get_risk_by_label(label):
    """
    DB 실제 라벨 기준 위험도.
    """

    if label == 1:
        return "고위험"
    elif label == 0:
        return "저위험"
    return "-"


def get_result_by_threshold(prob, threshold):
    return 1 if prob >= threshold else 0


def predict_with_ffnn(X):
    """
    scaler를 쓰지 않았으므로 X를 그대로 모델에 넣는다.
    """

    nr_er_prob = float(
        NR_ER_MODEL.predict(X, verbose=0)[0][0]
    )

    sr_p53_prob = float(
        SR_P53_MODEL.predict(X, verbose=0)[0][0]
    )

    return nr_er_prob, sr_p53_prob

def analyze_compound(input_smiles=None, input_name=None):
    """
    우선순위:
    1. smiles 값이 있으면 smiles로 분석
    2. smiles가 비어 있고 name 값이 있으면 PubChem API로 SMILES 변환 후 분석
    3. 분석에 사용한 SMILES로 PubChem에서 대표 name도 조회
    """

    input_smiles = "" if input_smiles is None else str(input_smiles).strip()
    input_name = "" if input_name is None else str(input_name).strip()

    # 1순위: SMILES가 있으면 SMILES 사용
    if input_smiles != "":
        result = analyze_smiles(input_smiles)

        # SMILES만 들어온 경우에도 대표 이름 조회
        resolved_name = input_name

        if resolved_name == "":
            pubchem_name, name_error = get_name_from_pubchem_smiles(
                result.get("canonical_smiles") or input_smiles
            )

            if name_error is None:
                resolved_name = pubchem_name

        result["input_smiles"] = input_smiles
        result["input_name"] = input_name
        result["input_type"] = "SMILES"
        result["resolved_name"] = resolved_name

        return result

    # 2순위: SMILES가 없고 name이 있으면 PubChem으로 SMILES 변환
    if input_name != "":
        converted_smiles, error = get_smiles_from_pubchem_name(input_name)

        if error is not None:
            return {
                "input_smiles": None,
                "input_name": input_name,
                "input_type": "NAME",
                "resolved_name": input_name,

                "canonical_smiles": None,
                "is_valid": False,

                "nr_er_source": "INVALID",
                "nr_er_result": None,
                "nr_er_prob": None,
                "nr_er_threshold": None,
                "nr_er_risk": "분석 불가",

                "sr_p53_source": "INVALID",
                "sr_p53_result": None,
                "sr_p53_prob": None,
                "sr_p53_threshold": None,
                "sr_p53_risk": "분석 불가",

                "message": f"name 변환 실패\n{error}",
            }

        result = analyze_smiles(converted_smiles)

        # name으로 들어온 경우도 PubChem 대표명으로 한 번 통일
        pubchem_name, name_error = get_name_from_pubchem_smiles(converted_smiles)

        if name_error is None:
            resolved_name = pubchem_name
        else:
            resolved_name = input_name

        result["input_smiles"] = converted_smiles
        result["input_name"] = input_name
        result["input_type"] = "NAME"
        result["resolved_name"] = resolved_name

        return result

    # 3순위: 둘 다 없음
    return {
        "input_smiles": None,
        "input_name": None,
        "input_type": "EMPTY",
        "resolved_name": None,

        "canonical_smiles": None,
        "is_valid": False,

        "nr_er_source": "INVALID",
        "nr_er_result": None,
        "nr_er_prob": None,
        "nr_er_threshold": None,
        "nr_er_risk": "분석 불가",

        "sr_p53_source": "INVALID",
        "sr_p53_result": None,
        "sr_p53_prob": None,
        "sr_p53_threshold": None,
        "sr_p53_risk": "분석 불가",

        "message": "smiles와 name이 모두 비어 있습니다.",
    }
    
def analyze_smiles(input_smiles):
    """
    하나의 SMILES를 분석한다.
    1. 유효성 검사
    2. canonical SMILES 변환
    3. DB 조회
    4. DB에 있으면 실제 라벨 사용
    5. DB에 없거나 해당 타깃 라벨이 없으면 FFNN 예측 사용
    """

    try:
        X, canonical_smiles = smiles_to_feature_dataframe(input_smiles)

    except ValueError as error:
        return {
            "input_smiles": input_smiles,
            "canonical_smiles": None,
            "is_valid": False,

            "nr_er_source": "INVALID",
            "nr_er_result": None,
            "nr_er_prob": None,
            "nr_er_threshold": None,
            "nr_er_risk": "분석 불가",

            "sr_p53_source": "INVALID",
            "sr_p53_result": None,
            "sr_p53_prob": None,
            "sr_p53_threshold": None,
            "sr_p53_risk": "분석 불가",

            "message": "SMILES 오류",
        }

    molecule = Molecule.objects.filter(
        canonical_smiles=canonical_smiles
    ).first()

    # 기본적으로 ML 예측값은 필요할 때만 계산
    nr_er_prob = None
    sr_p53_prob = None

    need_ml_for_nr_er = (
        molecule is None or molecule.nr_er is None
    )

    need_ml_for_sr_p53 = (
        molecule is None or molecule.sr_p53 is None
    )

    if need_ml_for_nr_er or need_ml_for_sr_p53:
        nr_er_prob, sr_p53_prob = predict_with_ffnn(X)

    # NR-ER 처리
    if molecule is not None and molecule.nr_er is not None:
        nr_er_source = "DB"
        nr_er_result = molecule.nr_er
        nr_er_prob_output = None
        nr_er_threshold = None
        nr_er_risk = get_risk_by_label(molecule.nr_er)
    else:
        nr_er_source = "ML"
        nr_er_result = get_result_by_threshold(
            nr_er_prob,
            NR_ER_THRESHOLD
        )
        nr_er_prob_output = round(nr_er_prob, 4)
        nr_er_threshold = NR_ER_THRESHOLD
        nr_er_risk = get_risk_by_prob(nr_er_prob)

    # SR-p53 처리
    if molecule is not None and molecule.sr_p53 is not None:
        sr_p53_source = "DB"
        sr_p53_result = molecule.sr_p53
        sr_p53_prob_output = None
        sr_p53_threshold = None
        sr_p53_risk = get_risk_by_label(molecule.sr_p53)
    else:
        sr_p53_source = "ML"
        sr_p53_result = get_result_by_threshold(
            sr_p53_prob,
            SR_P53_THRESHOLD
        )
        sr_p53_prob_output = round(sr_p53_prob, 4)
        sr_p53_threshold = SR_P53_THRESHOLD
        sr_p53_risk = get_risk_by_prob(sr_p53_prob)
    
    # if molecule is not None:
    #     message = "Tox21 DB에 존재하는 데이터입니다. 존재하는 라벨은 실제값을 출력했습니다."
    # else:
    #     message = "Tox21 DB에 없는 데이터이므로 FFNN 모델로 예측했습니다."

    def make_short_message(nr_er_source, sr_p53_source):
        source_label = {
            "DB": "실제값",
            "ML": "예측값",
            "INVALID": "분석 불가",
            "-": "-"
        }

        nr_text = source_label.get(nr_er_source, "-")
        sr_text = source_label.get(sr_p53_source, "-")

        return f"NR-ER: {nr_text} \nSR-p53: {sr_text}"
    
    message = make_short_message(
    nr_er_source,
    sr_p53_source
    )

    return {
        "input_smiles": input_smiles,
        "canonical_smiles": canonical_smiles,
        "is_valid": True,

        "nr_er_source": nr_er_source,
        "nr_er_result": nr_er_result,
        "nr_er_prob": nr_er_prob_output,
        "nr_er_threshold": nr_er_threshold,
        "nr_er_risk": nr_er_risk,

        "sr_p53_source": sr_p53_source,
        "sr_p53_result": sr_p53_result,
        "sr_p53_prob": sr_p53_prob_output,
        "sr_p53_threshold": sr_p53_threshold,
        "sr_p53_risk": sr_p53_risk,

        "message": message,
    }