import numpy as np
import pandas as pd

from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator, Descriptors
from rdkit.DataStructs import ConvertToNumpyArray

from .model_loader import FEATURE_COLUMNS


N_BITS = 2048
RADIUS = 3


morgan_generator = rdFingerprintGenerator.GetMorganGenerator(
    radius=RADIUS,
    fpSize=N_BITS
)


DESCRIPTOR_FUNCTIONS = {
    # 분자량 및 크기
    "desc_MolWt": Descriptors.MolWt,
    "desc_ExactMolWt": Descriptors.ExactMolWt,
    "desc_HeavyAtomMolWt": Descriptors.HeavyAtomMolWt,
    "desc_HeavyAtomCount": Descriptors.HeavyAtomCount,

    # 지용성 및 극성
    "desc_MolLogP": Descriptors.MolLogP,
    "desc_MolMR": Descriptors.MolMR,
    "desc_TPSA": Descriptors.TPSA,
    "desc_LabuteASA": Descriptors.LabuteASA,

    # 수소결합 및 원자 특성
    "desc_NumHDonors": Descriptors.NumHDonors,
    "desc_NumHAcceptors": Descriptors.NumHAcceptors,
    "desc_NHOHCount": Descriptors.NHOHCount,
    "desc_NOCount": Descriptors.NOCount,
    "desc_NumValenceElectrons": Descriptors.NumValenceElectrons,
    "desc_NumRadicalElectrons": Descriptors.NumRadicalElectrons,

    # 결합 및 구조 유연성
    "desc_NumRotatableBonds": Descriptors.NumRotatableBonds,
    "desc_FractionCSP3": Descriptors.FractionCSP3,

    # 전체 고리 및 고리 유형
    "desc_RingCount": Descriptors.RingCount,
    "desc_NumAromaticRings": Descriptors.NumAromaticRings,
    "desc_NumAliphaticRings": Descriptors.NumAliphaticRings,
    "desc_NumSaturatedRings": Descriptors.NumSaturatedRings,
    "desc_NumHeterocycles": Descriptors.NumHeterocycles,

    # 세부 고리 구조
    "desc_NumAromaticHeterocycles": Descriptors.NumAromaticHeterocycles,
    "desc_NumAromaticCarbocycles": Descriptors.NumAromaticCarbocycles,
    "desc_NumAliphaticHeterocycles": Descriptors.NumAliphaticHeterocycles,
    "desc_NumAliphaticCarbocycles": Descriptors.NumAliphaticCarbocycles,
    "desc_NumSaturatedHeterocycles": Descriptors.NumSaturatedHeterocycles,
    "desc_NumSaturatedCarbocycles": Descriptors.NumSaturatedCarbocycles,

    # 위상학적·구조 복잡성 지표
    "desc_BalabanJ": Descriptors.BalabanJ,
    "desc_BertzCT": Descriptors.BertzCT,
    "desc_HallKierAlpha": Descriptors.HallKierAlpha,
    "desc_Kappa1": Descriptors.Kappa1,
    "desc_Kappa2": Descriptors.Kappa2,
    "desc_Kappa3": Descriptors.Kappa3,

    # 약물 유사성 종합 지표
    "desc_QED": Descriptors.qed,
}


def to_mol_and_canonical(smiles):
    """
    SMILES를 RDKit Mol 객체와 canonical SMILES로 변환.
    invalid SMILES면 ValueError 발생.
    """

    if smiles is None:
        raise ValueError("SMILES가 비어 있습니다.")

    smiles = str(smiles).strip()

    if smiles == "":
        raise ValueError("SMILES가 비어 있습니다.")

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        raise ValueError("유효하지 않은 SMILES입니다.")

    canonical_smiles = Chem.MolToSmiles(
        mol,
        canonical=True
    )

    return mol, canonical_smiles


def mol_to_2d_descriptors(mol):
    descriptor_values = {}

    for descriptor_name, descriptor_func in DESCRIPTOR_FUNCTIONS.items():
        try:
            value = float(descriptor_func(mol))

            if not np.isfinite(value):
                value = np.nan

        except Exception:
            value = np.nan

        descriptor_values[descriptor_name] = value

    return descriptor_values


def mol_to_morgan_array(mol):
    fp = morgan_generator.GetFingerprint(mol)

    arr = np.zeros(
        N_BITS,
        dtype=np.int8
    )

    ConvertToNumpyArray(fp, arr)

    return arr


def smiles_to_feature_dataframe(smiles):
    """
    신규 SMILES를 FFNN 입력용 DataFrame으로 변환.
    최종 shape는 (1, 2082)가 되어야 함.
    """

    mol, canonical_smiles = to_mol_and_canonical(smiles)

    descriptor_dict = mol_to_2d_descriptors(mol)

    fingerprint_array = mol_to_morgan_array(mol)
    fingerprint_dict = {
        f"bit_{i}": int(fingerprint_array[i])
        for i in range(N_BITS)
    }

    feature_dict = {
        **fingerprint_dict,
        **descriptor_dict
    }

    X = pd.DataFrame([feature_dict])

    # 학습 때 저장한 feature 순서로 맞춤
    X = X.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0
    )

    # 혹시 descriptor 계산 실패로 NaN이 있으면 0으로 대체
    # 학습 때 별도 imputer를 안 썼다면 이 정도가 가장 단순함
    X = X.fillna(0)

    return X, canonical_smiles