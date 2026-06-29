from django.contrib import admin, messages
from django.utils.html import format_html
from .models import CSVUpload

from predictor.models import Molecule

from rdkit import Chem

import pandas as pd
import os


def read_csv_with_encoding(file_path):
    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr",
    ]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        f"CSV 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949 형식으로 저장해주세요. 오류: {last_error}"
    )


def normalize_column_name(column_name):
    return (
        str(column_name)
        .strip()
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )


def standardize_columns(df):
    column_aliases = {
        "name": [
            "name",
            "compoundname",
            "chemicalname",
            "moleculename",
        ],
        "smiles": [
            "smiles",
            "smile",
            "canonicalsmiles",
        ],
        "nr-er": [
            "nrer",
        ],
        "sr-p53": [
            "srp53",
            "p53",
        ],
    }

    normalized_columns = {}

    for original_column in df.columns:
        normalized = normalize_column_name(original_column)
        normalized_columns[normalized] = original_column

    rename_map = {}
    missing_columns = []

    for standard_name, aliases in column_aliases.items():
        found_column = None

        for alias in aliases:
            if alias in normalized_columns:
                found_column = normalized_columns[alias]
                break

        if found_column is None:
            missing_columns.append(standard_name)
        else:
            rename_map[found_column] = standard_name

    if missing_columns:
        raise ValueError(
            "❌ CSV 형식이 올바르지 않습니다.\n 필수 컬럼: Name, SMILES, NR-ER, SR-p53"
        )

    df = df.rename(columns=rename_map)

    return df[["name", "smiles", "nr-er", "sr-p53"]]


def clean_label(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        value = int(float(value))
    except ValueError:
        return None

    if value in [0, 1]:
        return value

    return None


def to_canonical_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return None

    return Chem.MolToSmiles(mol, canonical=True)


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = (
        "file",
        "uploaded_at",
        "delete_button",
    )

    ordering = (
        "-uploaded_at",
    )

    list_filter = (
        "uploaded_at",
    )

    search_fields = (
        "file",
    )

    def delete_button(self, obj):
        return format_html(
            '<a class="btn btn-danger btn-sm" href="/admin/admin_csvmanager/csvupload/{}/delete/">삭제</a>',
            obj.id,
        )

    delete_button.short_description = "삭제"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        try:
            df = read_csv_with_encoding(obj.file.path)
            df = standardize_columns(df)

            new_count = 0
            update_count = 0
            skip_count = 0

            for _, row in df.iterrows():
                name = "" if pd.isna(row["name"]) else str(row["name"]).strip()
                smiles = "" if pd.isna(row["smiles"]) else str(row["smiles"]).strip()

                if smiles == "":
                    skip_count += 1
                    continue

                canonical_smiles = to_canonical_smiles(smiles)

                if canonical_smiles is None:
                    skip_count += 1
                    continue

                nr_er = clean_label(row["nr-er"])
                sr_p53 = clean_label(row["sr-p53"])

                molecule, created = Molecule.objects.update_or_create(
                    canonical_smiles=canonical_smiles,
                    defaults={
                        "name": name,
                        "smiles": smiles,
                        "nr_er": nr_er,
                        "sr_p53": sr_p53,
                    }
                )

                if created:
                    new_count += 1
                else:
                    update_count += 1

            self.message_user(
                request,
                f"""
✅ CSV 업로드 완료

신규 저장 : {new_count}건
업데이트 : {update_count}건
스킵 : {skip_count}건
총 처리 : {new_count + update_count}건
""",
                level=messages.SUCCESS,
            )

        except Exception as e:
            self.message_user(
                request,
                f"❌ 업로드 실패 : {e}",
                level=messages.ERROR,
            )

    def delete_model(self, request, obj):
        if obj.file:
            if os.path.isfile(obj.file.path):
                os.remove(obj.file.path)

        super().delete_model(request, obj)
        
