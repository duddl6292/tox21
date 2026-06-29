import json
from io import BytesIO

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Draw


def ketcher(request):
    return render(request, "editor/ketcher.html")


@csrf_exempt
def get_formula(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST 요청만 허용됩니다."},
            status=405
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "잘못된 요청 데이터입니다."},
            status=400
        )

    smiles = data.get("smiles")

    if not smiles:
        return JsonResponse(
            {"error": "SMILES 값이 없습니다."},
            status=400
        )

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return JsonResponse(
            {"error": "잘못된 SMILES입니다."},
            status=400
        )

    formula = rdMolDescriptors.CalcMolFormula(mol)

    return JsonResponse({
        "formula": formula
    })


@csrf_exempt
def download_png(request):
    # POST 요청만 허용
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST 요청만 허용됩니다."},
            status=405
        )

    # 로그인한 사용자만 다운로드 가능
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "PNG 다운로드는 로그인 후 이용 가능합니다."},
            status=403
        )

    # JSON 데이터 읽기
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "잘못된 요청 데이터입니다."},
            status=400
        )

    smiles = data.get("smiles")

    if not smiles:
        return JsonResponse(
            {"error": "SMILES 값이 없습니다."},
            status=400
        )

    # SMILES → RDKit Mol 변환
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return JsonResponse(
            {"error": "잘못된 SMILES입니다."},
            status=400
        )

    # 분자 구조 PNG 이미지 생성
    image = Draw.MolToImage(
        mol,
        size=(600, 450)
    )

    # 메모리에 PNG 저장
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # 다운로드 응답 생성
    response = HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )

    response["Content-Disposition"] = 'attachment; filename="molecule.png"'

    return response