from django.contrib import admin
from .models import Tox21Chemical


@admin.register(Tox21Chemical)
class Tox21ChemicalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_smiles",
        "nr_er",
        "sr_p53",
        "created_at",
    )

    search_fields = (
        "name",
        "smiles",
        "canonical_smiles",
    )

    list_filter = (
        "nr_er",
        "sr_p53",
        "created_at",
    )

    readonly_fields = (
        "canonical_smiles",
        "created_at",
    )

    fields = (
        "name",
        "smiles",
        "canonical_smiles",
        "nr_er",
        "sr_p53",
        "created_at",
    )

    ordering = (
        "-created_at",
    )
    def short_smiles(self, obj):
        if obj.smiles and len(obj.smiles) > 60:
            return obj.smiles[:60] + "..."
        return obj.smiles

    short_smiles.short_description = "SMILES"
    
    