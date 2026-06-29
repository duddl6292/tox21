import csv
import re
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from rdkit import Chem
from rdkit.Chem import Draw

from .models import Molecule, AnalysisJob, AnalysisResult
from .ml.predict_service import analyze_compound
import io
from .forms import CSVUploadForm

def make_safe_csv_filename(filename, default_name):
    """
    사용자가 입력한 파일명을 안전한 CSV 파일명으로 변환한다.
    """

    filename = "" if filename is None else str(filename).strip()

    if filename == "":
        filename = default_name

    # 윈도우 파일명에서 사용할 수 없는 문자 제거
    filename = re.sub(r'[\\/:*?"<>|\r\n]', "_", filename)

    # 앞뒤 공백, 점 제거
    filename = filename.strip().strip(".")

    if filename == "":
        filename = default_name

    # 확장자가 없으면 .csv 추가
    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    return filename

def decode_uploaded_csv(uploaded_file):
    """
    업로드된 CSV를 문자열로 디코딩.
    utf-8-sig 우선, 실패하면 cp949 시도.
    """

    raw_data = uploaded_file.read()

    try:
        decoded = raw_data.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = raw_data.decode("cp949")

    return decoded


def find_smiles_column(fieldnames):
    """
    CSV 컬럼 중 smiles 컬럼을 대소문자 구분 없이 찾는다.
    """

    if fieldnames is None:
        return None

    for fieldname in fieldnames:
        if fieldname.strip().lower() == "smiles":
            return fieldname

    return None

def find_name_column(fieldnames):
    """
    CSV 컬럼 중 name 컬럼을 대소문자 구분 없이 찾는다.
    """

    if fieldnames is None:
        return None

    for fieldname in fieldnames:
        if fieldname.strip().lower() == "name":
            return fieldname

    return None

def upload_csv(request):
    """
    CSV 업로드 및 대량 분석.
    로그인하지 않은 사람도 분석 결과 페이지는 볼 수 있다.
    단, CSV 다운로드는 로그인한 사람만 가능.
    """

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]

            try:
                decoded_file = decode_uploaded_csv(csv_file)
            except UnicodeDecodeError:
                return render(
                    request,
                    "predictor/upload.html",
                    {
                        "form": form,
                        "error": "CSV 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949 형식으로 저장해주세요.",
                    }
                )

            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            smiles_column = find_smiles_column(reader.fieldnames)
            name_column = find_name_column(reader.fieldnames)

            if smiles_column is None and name_column is None:
                return render(
                    request,
                    "predictor/upload.html",
                    {
                        "form": form,
                        "error": "CSV 파일에 smiles 또는 name 컬럼이 필요합니다.",
                    }
                )

            job = AnalysisJob.objects.create(
                user=request.user if request.user.is_authenticated else None,
                file_name=csv_file.name
            )

            total_count = 0
            success_count = 0
            error_count = 0

            for row_number, row in enumerate(reader, start=1):
                total_count += 1

                input_smiles = ""
                input_name = ""

                if smiles_column is not None:
                    input_smiles = row.get(smiles_column, "")
                    input_smiles = str(input_smiles).strip()

                if name_column is not None:
                    input_name = row.get(name_column, "")
                    input_name = str(input_name).strip()

                result = analyze_compound(
                    input_smiles=input_smiles,
                    input_name=input_name
                )

                AnalysisResult.objects.create(
                    job=job,
                    row_number=row_number,
                    input_smiles=result["input_smiles"],
                    input_name=result.get("input_name"),
                    input_type=result.get("input_type"),
                    resolved_name=result.get("resolved_name"),
                    canonical_smiles=result["canonical_smiles"],
                    is_valid=result["is_valid"],

                    nr_er_source=result["nr_er_source"],
                    nr_er_result=result["nr_er_result"],
                    nr_er_prob=result["nr_er_prob"],
                    nr_er_threshold=result["nr_er_threshold"],
                    nr_er_risk=result["nr_er_risk"],

                    sr_p53_source=result["sr_p53_source"],
                    sr_p53_result=result["sr_p53_result"],
                    sr_p53_prob=result["sr_p53_prob"],
                    sr_p53_threshold=result["sr_p53_threshold"],
                    sr_p53_risk=result["sr_p53_risk"],

                    message=result["message"],
                )

                if result["is_valid"]:
                    success_count += 1
                else:
                    error_count += 1

            job.total_count = total_count
            job.success_count = success_count
            job.error_count = error_count
            job.save()

            return redirect(
                "predictor:result_list",
                job_id=job.id
            )

    else:
        form = CSVUploadForm()

    return render(
        request,
        "predictor/upload.html",
        {
            "form": form
        }
    )


def result_list(request, job_id):
    job = get_object_or_404(AnalysisJob, id=job_id)

    results = job.results.all().order_by("row_number")

    summary = {
        "total": results.count(),
        "success": results.filter(is_valid=True).count(),
        "error": results.filter(is_valid=False).count(),

        "nr_er_high": results.filter(nr_er_risk="고위험").count(),
        "nr_er_mid": results.filter(nr_er_risk="중위험").count(),
        "nr_er_low": results.filter(nr_er_risk="저위험").count(),

        "sr_p53_high": results.filter(sr_p53_risk="고위험").count(),
        "sr_p53_mid": results.filter(sr_p53_risk="중위험").count(),
        "sr_p53_low": results.filter(sr_p53_risk="저위험").count(),

        "db_count": results.filter(
            Q(nr_er_source="DB") | Q(sr_p53_source="DB")
        ).count(),

        "ml_count": results.filter(
            Q(nr_er_source="ML") | Q(sr_p53_source="ML")
        ).count(),
    }

    return render(
        request,
        "predictor/result_list.html",
        {
            "job": job,
            "results": results,
            "summary": summary,
        }
    )


@login_required
def download_result_csv(request, job_id):
    """
    분석 결과 CSV 다운로드.
    로그인한 사용자만 접근 가능.
    """

    job = get_object_or_404(
        AnalysisJob,
        id=job_id
    )

    results = job.results.all()

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    raw_filename = request.GET.get("filename")

    filename = make_safe_csv_filename(
        raw_filename,
        default_name=f"tox21_analysis_{job.id}"
    )

    response["Content-Disposition"] = (
        f"attachment; filename*=UTF-8''{quote(filename)}"
    )

    # Excel 한글 깨짐 방지용 BOM
    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "row_number",
        "resolved_name",
        # "input_name",
        # "input_type",
        "input_smiles",
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
    ])

    for result in results:
        writer.writerow([
            result.row_number,
            result.resolved_name,
            # result.input_name,
            # result.input_smiles,
            result.canonical_smiles,

            result.nr_er_source,
            result.nr_er_result,
            result.nr_er_prob,
            result.nr_er_threshold,
            result.nr_er_risk,

            result.sr_p53_source,
            result.sr_p53_result,
            result.sr_p53_prob,
            result.sr_p53_threshold,
            result.sr_p53_risk,

            result.message,
        ])

    return response
@login_required
def history(request):
    jobs = (
        AnalysisJob.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "predictor/history.html",
        {
            "jobs": jobs,
        }
    )
def single_analyze(request):
    result = None
    compound_input = ""
    input_mode = "auto"

    # 검색 페이지에서 넘어온 경우
    if request.method == "GET":
        compound_input = request.GET.get("q", "").strip()
        input_mode = request.GET.get("mode", "auto").strip()

        if compound_input:
            result = run_single_analysis(compound_input, input_mode)

    # 직접 입력한 경우
    if request.method == "POST":
        compound_input = request.POST.get("compound_input", "").strip()
        input_mode = request.POST.get("input_mode", "auto").strip()

        if compound_input:
            result = run_single_analysis(compound_input, input_mode)

    return render(
        request,
        "predictor/single_analyze.html",
        {
            "result": result,
            "compound_input": compound_input,
            "input_mode": input_mode,
        }
    )


def run_single_analysis(compound_input, input_mode):
    """
    단일 입력값을 name 또는 SMILES로 판단해서 분석한다.
    """

    if input_mode == "smiles":
        return analyze_compound(
            input_smiles=compound_input,
            input_name=""
        )

    if input_mode == "name":
        return analyze_compound(
            input_smiles="",
            input_name=compound_input
        )

    # auto 모드
    mol = Chem.MolFromSmiles(compound_input)

    if mol is not None:
        return analyze_compound(
            input_smiles=compound_input,
            input_name=""
        )

    return analyze_compound(
        input_smiles="",
        input_name=compound_input
    )
def search_molecule(request):
    query = request.GET.get("q", "").strip()

    molecules = Molecule.objects.none()

    if query:
        molecules = (
            Molecule.objects
            .filter(
                Q(name__icontains=query) |
                Q(smiles__icontains=query) |
                Q(canonical_smiles__icontains=query)
            )
            .order_by("name", "id")[:100]
        )

    return render(
        request,
        "predictor/search.html",
        {
            "query": query,
            "molecules": molecules,
        }
    )
def smiles_to_svg_response(smiles):
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return HttpResponse(
            "Invalid SMILES",
            status=400,
            content_type="text/plain"
        )

    svg = Draw.MolsToGridImage(
        [mol],
        molsPerRow=1,
        subImgSize=(250, 200),
        useSVG=True
    )

    return HttpResponse(
        svg,
        content_type="image/svg+xml"
    )


def result_structure_image(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id)

    smiles = result.canonical_smiles or result.input_smiles

    if not smiles:
        return HttpResponse(
            "No SMILES",
            status=404,
            content_type="text/plain"
        )

    return smiles_to_svg_response(smiles)


def molecule_structure_image(request, molecule_id):
    molecule = get_object_or_404(Molecule, id=molecule_id)

    smiles = molecule.canonical_smiles or molecule.smiles

    if not smiles:
        return HttpResponse(
            "No SMILES",
            status=404,
            content_type="text/plain"
        )

    return smiles_to_svg_response(smiles)
def about(request):
    return render(
        request,
        "predictor/about.html"
    )