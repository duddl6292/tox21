from django import forms
from .models import Chemical


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = Chemical
        fields = ["name", "formula", "smiles", "toxicity", "description"]


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV 파일")