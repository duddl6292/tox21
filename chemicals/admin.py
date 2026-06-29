# import csv

# from django.contrib import admin
# from django.http import HttpResponse

# from .models import (
#     Chemical,
#     ChemicalCategory,
#     ToxicityEndpoint,
#     CSVUploadHistory,
#     PredictionHistory,
#     DatasetVersion,
#     Notice,
#     ChemicalNews,
#     MainBanner,
#     Inquiry,
#     FAQ,
# )


# @admin.register(ChemicalCategory)
# class ChemicalCategoryAdmin(admin.ModelAdmin):
#     list_display = ["id", "name", "description"]
#     search_fields = ["name", "description"]


# @admin.register(ToxicityEndpoint)
# class ToxicityEndpointAdmin(admin.ModelAdmin):
#     list_display = ["id", "name", "is_active", "description"]
#     list_filter = ["is_active"]
#     search_fields = ["name", "description"]


# @admin.register(Chemical)
# class ChemicalAdmin(admin.ModelAdmin):
#     list_display = ["id", "name", "formula", "smiles", "toxicity", "category", "endpoint", "created_at"]
#     search_fields = ["name", "formula", "smiles", "toxicity", "description"]
#     list_filter = ["toxicity", "category", "endpoint", "created_at"]
#     ordering = ["-id"]
#     readonly_fields = ["created_at"]
#     actions = ["export_as_csv"]

#     def export_as_csv(self, request, queryset):
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="chemicals.csv"'

#         writer = csv.writer(response)
#         writer.writerow(["name", "formula", "smiles", "toxicity", "category", "endpoint", "description", "created_at"])

#         for chemical in queryset:
#             writer.writerow([
#                 chemical.name,
#                 chemical.formula,
#                 chemical.smiles,
#                 chemical.toxicity,
#                 chemical.category,
#                 chemical.endpoint,
#                 chemical.description,
#                 chemical.created_at,
#             ])

#         return response

#     export_as_csv.short_description = "선택한 화학식 CSV 다운로드"


# @admin.register(CSVUploadHistory)
# class CSVUploadHistoryAdmin(admin.ModelAdmin):
#     list_display = ["id", "file_name", "uploaded_by", "total_count", "success_count", "fail_count", "uploaded_at"]
#     list_filter = ["uploaded_at"]
#     search_fields = ["file_name", "uploaded_by__username"]
#     ordering = ["-uploaded_at"]


# @admin.register(PredictionHistory)
# class PredictionHistoryAdmin(admin.ModelAdmin):
#     list_display = ["id", "user", "smiles", "endpoint", "prediction_result", "probability", "created_at"]
#     list_filter = ["prediction_result", "endpoint", "created_at"]
#     search_fields = ["user__username", "smiles", "prediction_result"]
#     ordering = ["-created_at"]


# @admin.register(DatasetVersion)
# class DatasetVersionAdmin(admin.ModelAdmin):
#     list_display = ["id", "version_name", "is_active", "created_at"]
#     list_filter = ["is_active", "created_at"]
#     search_fields = ["version_name", "description"]


# @admin.register(Notice)
# class NoticeAdmin(admin.ModelAdmin):
#     list_display = ["id", "title", "writer", "is_visible", "created_at", "updated_at"]
#     list_filter = ["is_visible", "created_at"]
#     search_fields = ["title", "content", "writer__username"]
#     ordering = ["-created_at"]


# @admin.register(ChemicalNews)
# class ChemicalNewsAdmin(admin.ModelAdmin):
#     list_display = ["id", "title", "source", "is_visible", "created_at"]
#     list_filter = ["is_visible", "source", "created_at"]
#     search_fields = ["title", "source", "link"]
#     ordering = ["-created_at"]


# @admin.register(MainBanner)
# class MainBannerAdmin(admin.ModelAdmin):
#     list_display = ["id", "title", "order", "is_active"]
#     list_filter = ["is_active"]
#     search_fields = ["title", "subtitle"]
#     ordering = ["order"]


# @admin.register(Inquiry)
# class InquiryAdmin(admin.ModelAdmin):
#     list_display = ["id", "name", "email", "title", "is_answered", "created_at"]
#     list_filter = ["is_answered", "created_at"]
#     search_fields = ["name", "email", "title", "content"]
#     ordering = ["-created_at"]


# @admin.register(FAQ)
# class FAQAdmin(admin.ModelAdmin):
#     list_display = ["id", "question", "order", "is_visible"]
#     list_filter = ["is_visible"]
#     search_fields = ["question", "answer"]
#     ordering = ["order"]