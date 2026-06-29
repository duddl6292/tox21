# from django.contrib import admin

# from .models import Molecule, AnalysisJob, AnalysisResult


# @admin.register(Molecule)
# class MoleculeAdmin(admin.ModelAdmin):
#     fields = (
#         "name",
#         "smiles",
#         "nr_er",
#         "sr_p53",
#     )

#     list_display = (
#         "id",
#         "name",
#         "short_smiles",
#         "nr_er",
#         "sr_p53",
#         "created_at",
#     )

#     search_fields = (
#         "name",
#         "smiles",
#         "canonical_smiles",
#     )

#     list_filter = (
#         "nr_er",
#         "sr_p53",
#     )

#     def short_smiles(self, obj):
#         if len(obj.smiles) > 50:
#             return obj.smiles[:50] + "..."
#         return obj.smiles

#     short_smiles.short_description = "SMILES"


# @admin.register(AnalysisJob)
# class AnalysisJobAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "file_name",
#         "user",
#         "total_count",
#         "success_count",
#         "error_count",
#         "created_at",
#     )

#     search_fields = (
#         "file_name",
#         "user__username",
#     )

#     list_filter = (
#         "created_at",
#     )


# @admin.register(AnalysisResult)
# class AnalysisResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "job",
#         "row_number",
#         "resolved_name",
#         "input_type",
#         "nr_er_source",
#         "nr_er_result",
#         "nr_er_risk",
#         "sr_p53_source",
#         "sr_p53_result",
#         "sr_p53_risk",
#     )

#     search_fields = (
#         "input_name",
#         "resolved_name",
#         "input_smiles",
#         "canonical_smiles",
#     )

#     list_filter = (
#         "input_type",
#         "nr_er_source",
#         "nr_er_risk",
#         "sr_p53_source",
#         "sr_p53_risk",
#     )