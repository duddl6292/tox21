from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout,  update_session_auth_hash
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from .models import Profile
from .forms import SignupForm, UserUpdateForm, ProfileUpdateForm


def is_admin(user):
    return user.is_staff


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(
                user=user,
                phone=form.cleaned_data.get("phone"),
                company=form.cleaned_data.get("company"),
                address=form.cleaned_data.get("address"),
            )

            login(request, user)
            return redirect("home")

    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})

@login_required
def mypage(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "profile_submit" in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, instance=profile)
            password_form = PasswordChangeForm(request.user)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "개인정보가 수정되었습니다.")
                return redirect("accounts:mypage")

        elif "password_submit" in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)
            password_form = PasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                profile.password_reset_required = False
                profile.save()

                messages.success(request, "비밀번호가 변경되었습니다.")
                return redirect("accounts:mypage")

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        password_form = PasswordChangeForm(request.user)

    return render(request, "accounts/mypage.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "password_form": password_form,
        "profile": profile,
    })


@login_required
def user_delete(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("home")

    return render(request, "accounts/user_confirm_delete.html")


@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "accounts/admin_user_list.html", {"users": users})


@user_passes_test(is_admin)
def admin_user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=user_obj)

    return render(request, "accounts/admin_user_detail.html", {
        "user_obj": user_obj,
        "profile": profile,
    })


@user_passes_test(is_admin)
def admin_user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=user_obj)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user_obj)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "회원정보가 수정되었습니다.")
            return redirect("accounts:admin_user_detail", pk=user_obj.pk)

    else:
        user_form = UserUpdateForm(instance=user_obj)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/admin_user_update.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "user_obj": user_obj,
    })


@user_passes_test(is_admin)
def admin_password_reset(request, pk): # 비밀번호 초기화 시 알림 + 비밀번호 재설정 기능
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user_obj.set_password("1234")
        user_obj.save()

        profile, created = Profile.objects.get_or_create(user=user_obj)
        profile.password_reset_required = True
        profile.save()

        messages.success(request, "비밀번호가 1234로 초기화되었습니다.")
        return redirect("accounts:admin_user_detail", pk=user_obj.pk)

    return render(request, "accounts/admin_password_reset.html", {
        "user_obj": user_obj,
    })


@user_passes_test(is_admin)
def admin_user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "회원이 삭제되었습니다.")
        return redirect("accounts:admin_user_list")

    return render(request, "accounts/admin_user_delete.html", {
        "user_obj": user_obj,
    })

@login_required
def delete_account(request):
 
    if request.method == 'POST':
        input_password = request.POST.get('password')
        user = request.user
       
        if user.check_password(input_password):
            user.delete()      
            logout(request)    
           
            return redirect('home')
        else:
            messages.error(request, "비밀번호가 일치하지 않습니다. 다시 확인해 주세요.")
           
    return render(request, 'accounts/delete.html')
