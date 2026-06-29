import re
import requests
from functools import lru_cache
from urllib.parse import quote


HEADERS = {
    "User-Agent": "Tox21-Django-Project/1.0"
}


def _choose_best_synonym(synonyms):
    """
    PubChem synonym 목록에서 화면에 보여주기 좋은 이름을 하나 고른다.
    """

    if not synonyms:
        return None

    bad_prefixes = [
        "SCHEMBL",
        "CHEMBL",
        "DTXSID",
        "DTXCID",
        "AKOS",
        "ZINC",
        "NSC",
        "MLS",
        "CID",
    ]

    cas_pattern = re.compile(r"^\d{2,7}-\d{2}-\d$")

    for synonym in synonyms:
        name = str(synonym).strip()

        if name == "":
            continue

        if len(name) > 80:
            continue

        if cas_pattern.match(name):
            continue

        upper_name = name.upper()

        if any(upper_name.startswith(prefix) for prefix in bad_prefixes):
            continue

        if any(char.isalpha() for char in name):
            return name

    return str(synonyms[0]).strip()


@lru_cache(maxsize=1000)
def get_name_from_pubchem_smiles(smiles):
    """
    PubChem API를 이용해 SMILES로 대표 화합물명을 조회한다.

    처리 흐름:
    1. SMILES -> CID 조회
    2. CID -> synonyms 조회
    3. 보기 좋은 synonym 하나 선택

    성공: (name, None)
    실패: (None, error_message)
    """

    smiles = "" if smiles is None else str(smiles).strip()

    if smiles == "" or smiles.lower() in ["none", "nan"]:
        return None, "SMILES가 비어 있습니다."

    try:
        # 1단계: SMILES -> CID
        # SMILES에는 /, #, + 같은 문자가 들어갈 수 있어서 POST 방식이 더 안전함
        cid_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/cids/TXT"

        cid_response = requests.post(
            cid_url,
            data={"smiles": smiles},
            headers=HEADERS,
            timeout=10
        )

        if cid_response.status_code == 404:
            return None, "PubChem에서 해당 SMILES를 찾을 수 없습니다."

        cid_response.raise_for_status()

        cid_lines = [
            line.strip()
            for line in cid_response.text.splitlines()
            if line.strip()
        ]

        if not cid_lines:
            return None, "PubChem에서 CID를 찾을 수 없습니다."

        cid = cid_lines[0]

        # 2단계: CID -> synonym 조회
        synonym_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
            f"compound/cid/{cid}/synonyms/JSON"
        )

        synonym_response = requests.get(
            synonym_url,
            headers=HEADERS,
            timeout=10
        )

        synonym_response.raise_for_status()

        data = synonym_response.json()

        infos = data.get("InformationList", {}).get("Information", [])

        if not infos:
            return None, "PubChem 응답에서 synonym 정보를 찾을 수 없습니다."

        synonyms = infos[0].get("Synonym", [])

        name = _choose_best_synonym(synonyms)

        if name:
            return name, None

        return None, "PubChem synonym 목록에서 적절한 이름을 찾을 수 없습니다."

    except requests.exceptions.Timeout:
        return None, "PubChem API 응답 시간이 초과되었습니다."

    except requests.exceptions.RequestException as e:
        return None, f"PubChem API 요청 중 오류가 발생했습니다: {e}"

    except ValueError:
        return None, "PubChem 응답 JSON을 해석할 수 없습니다."


def get_smiles_from_pubchem_name(compound_name):
    """
    PubChem PUG-REST API를 이용해 화합물명으로 SMILES를 조회한다.

    처리 흐름:
    1. compound name -> CID 조회
    2. CID -> SMILES 조회

    성공: (smiles, None)
    실패: (None, error_message)
    """

    compound_name = "" if compound_name is None else str(compound_name).strip()

    if compound_name == "" or compound_name.lower() in ["none", "nan"]:
        return None, "화합물명이 비어 있습니다."

    encoded_name = quote(compound_name, safe="")

    headers = {
        "User-Agent": "Tox21-Django-Project/1.0"
    }

    try:
        # 1단계: name -> CID
        cid_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
            f"compound/name/{encoded_name}/cids/TXT"
        )

        cid_response = requests.get(
            cid_url,
            headers=headers,
            timeout=10
        )

        if cid_response.status_code == 404:
            return None, "PubChem에서 해당 화합물명을 찾을 수 없습니다."

        cid_response.raise_for_status()

        cid_lines = [
            line.strip()
            for line in cid_response.text.splitlines()
            if line.strip()
        ]

        if not cid_lines:
            return None, "PubChem에서 CID를 찾을 수 없습니다."

        cid = cid_lines[0]

        # 2단계: CID -> SMILES
        property_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
            f"compound/cid/{cid}/property/"
            "CanonicalSMILES,IsomericSMILES/JSON"
        )

        property_response = requests.get(
            property_url,
            headers=headers,
            timeout=10
        )

        property_response.raise_for_status()

        data = property_response.json()

        properties = data.get("PropertyTable", {}).get("Properties", [])

        if not properties:
            return None, "PubChem 응답에서 화합물 속성을 찾을 수 없습니다."

        compound_data = properties[0]

        # 네 응답에서는 SMILES / ConnectivitySMILES로 들어오고 있음
        smiles = (
            compound_data.get("SMILES")
            or compound_data.get("ConnectivitySMILES")
            or compound_data.get("CanonicalSMILES")
            or compound_data.get("IsomericSMILES")
        )

        if not smiles:
            return None, (
                "PubChem 응답에서 SMILES를 찾을 수 없습니다. "
                f"응답 key: {list(compound_data.keys())}"
            )

        return smiles, None

    except requests.exceptions.Timeout:
        return None, "PubChem API 응답 시간이 초과되었습니다."

    except requests.exceptions.RequestException as e:
        return None, f"PubChem API 요청 중 오류가 발생했습니다: {e}"

    except ValueError:
        return None, "PubChem 응답 JSON을 해석할 수 없습니다."