from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import CreateUserForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = "/"


@user_passes_test(lambda u: u.is_superuser)
def create_user_view(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:create_user")
    else:
        form = CreateUserForm()

    return render(request, "accounts/create_user.html", {"form": form})
