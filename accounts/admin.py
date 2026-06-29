from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered

from .models import Profile, LoginHistory, AdminActionLog


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    list_display = ["id", "username", "email", "is_staff", "is_superuser", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined"]
    search_fields = ["username", "email", "profile__phone", "profile__company"]
    actions = ["reset_password_to_1234"]

    def reset_password_to_1234(self, request, queryset):
        for user in queryset:
            user.set_password("1234")
            user.save()

        self.message_user(request, "선택한 회원의 비밀번호가 1234로 초기화되었습니다.")

    reset_password_to_1234.short_description = "선택 회원 비밀번호 1234로 초기화"


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "phone", "company", "address"]
    search_fields = ["user__username", "user__email", "phone", "company", "address"]


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "ip_address", "browser", "login_time", "success"]
    list_filter = ["success", "login_time"]
    search_fields = ["user__username", "ip_address", "browser"]
    ordering = ["-login_time"]


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ["id", "admin_user", "action", "target_model", "target_object", "created_at"]
    list_filter = ["target_model", "created_at"]
    search_fields = ["admin_user__username", "action", "target_model", "target_object"]
    ordering = ["-created_at"]