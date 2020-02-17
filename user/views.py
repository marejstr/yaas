from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import translation
from django.views import View
from rest_framework.authtoken.models import Token

from .forms import EditAccountForm, RegisterUserForm


class SignUp(View):
    def get(self, request):
        form = RegisterUserForm()
        return render(request, "registration.html", {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            if not (username and email and password):
                messages.error(request, 'username, email or password missing')
                return render(request, "registration.html", {'form': form})

            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username has been taken')
                return render(request, "registration.html", {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email has been taken')
                return render(request, "registration.html", {'form': form})

            user = User.objects.create_user(username, email, password)
            if user is not None:
                login(request, user)

            return redirect("index")

        else:
            return render(request, "registration.html", {'form': form})


class SignIn(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', reverse("index"))
        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)

            translation.activate(user.userlanguage.language)
            request.session[
                translation.LANGUAGE_SESSION_KEY] = user.userlanguage.language
            request.session['currency'] = user.usercurrency.currency
            request.session.modified = True

            return HttpResponseRedirect(nextTo)
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid username or password")
            return HttpResponseRedirect(reverse("signin"))


def signout(request):
    logout(request)
    return redirect("index")


class EditProfile(View):
    def get(self, request):
        if request.user.is_authenticated:

            form = EditAccountForm()
            token = Token.objects.get_or_create(user=request.user)
            user_token = token[0]
            return render(request, "edit.html", {
                'form': form,
                'user_token': user_token
            })
        else:
            return redirect("signin")

    def post(self, request):
        form = EditAccountForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email has been taken')
                return render(request, "edit.html", {'form': form})

            current_user = request.user

            if password is not "":
                current_user.set_password(password)

            if email is not "":
                current_user.email = email

            current_user.save()

            return redirect("index")

        else:
            return render(request, "edit.html", {'form': form})
