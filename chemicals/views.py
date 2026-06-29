import csv
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from .models import Chemical
from .forms import ChemicalForm, CSVUploadForm


def is_admin(user):
    return user.is_staff

# #############################################################################
# @user_passes_test(is_admin)
def chemical_list(request):
    chemicals = Chemical.objects.all().order_by("-id")
    return render(request, "chemicals/chemical_list.html", {
        "chemicals": chemicals,
    })
# #############################################################################

@user_passes_test(is_admin)
def chemical_create(request):
    if request.method == "POST":
        form = ChemicalForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "화학식 정보가 등록되었습니다.")
            return redirect("chemicals:chemical_list")

    else:
        form = ChemicalForm()

    return render(request, "chemicals/chemical_form.html", {
        "form": form,
    })


@user_passes_test(is_admin)
def chemical_update(request, pk):
    chemical = get_object_or_404(Chemical, pk=pk)

    if request.method == "POST":
        form = ChemicalForm(request.POST, instance=chemical)

        if form.is_valid():
            form.save()
            messages.success(request, "화학식 정보가 수정되었습니다.")
            return redirect("chemicals:chemical_list")

    else:
        form = ChemicalForm(instance=chemical)

    return render(request, "chemicals/chemical_form.html", {
        "form": form,
        "chemical": chemical,
    })


@user_passes_test(is_admin)
def chemical_delete(request, pk):
    chemical = get_object_or_404(Chemical, pk=pk)

    if request.method == "POST":
        chemical.delete()
        messages.success(request, "화학식 정보가 삭제되었습니다.")
        return redirect("chemicals:chemical_list")

    return render(request, "chemicals/chemical_confirm_delete.html", {
        "chemical": chemical,
    })


@user_passes_test(is_admin)
def chemical_csv_upload(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            decoded_file = csv_file.read().decode("utf-8-sig")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            count = 0

            for row in reader:
                Chemical.objects.update_or_create(
                    name=row.get("name", ""),
                    defaults={
                        "formula": row.get("formula", ""),
                        "smiles": row.get("smiles", ""),
                        "toxicity": row.get("toxicity", ""),
                        "description": row.get("description", ""),
                    }
                )
                count += 1

            messages.success(request, f"CSV 데이터 {count}개가 업데이트되었습니다.")
            return redirect("chemicals:chemical_list")

    else:
        form = CSVUploadForm()

    return render(request, "chemicals/chemical_csv_upload.html", {
        "form": form,
    })