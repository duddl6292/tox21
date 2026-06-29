from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model): # 마이페이지 내용설정!
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("전화번호", max_length=20, blank=True)
    company = models.CharField("소속", max_length=100, blank=True)
    address = models.CharField("주소", max_length=200, blank=True)
    password_reset_required = models.BooleanField("비밀번호 초기화 여부", default=False)

    def __str__(self):
        return self.user.username


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="사용자")
    ip_address = models.CharField("IP 주소", max_length=50, blank=True)
    browser = models.CharField("브라우저", max_length=200, blank=True)
    login_time = models.DateTimeField("로그인 시간", auto_now_add=True)
    success = models.BooleanField("성공 여부", default=True)

    def __str__(self):
        return f"{self.user} - {self.login_time}"


class AdminActionLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="관리자")
    action = models.CharField("작업 내용", max_length=200)
    target_model = models.CharField("대상 모델", max_length=100, blank=True)
    target_object = models.CharField("대상 객체", max_length=200, blank=True)
    created_at = models.DateTimeField("작업 시간", auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user} - {self.action}"