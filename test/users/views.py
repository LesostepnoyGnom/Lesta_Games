from http.server import HTTPServer

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages

from .forms import LoginUserForm, RegisterUserForm, PasswordForm, PasswordChangeForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

@login_required
def logout_user(request):

    logout(request)

    return HttpResponseRedirect(reverse('users:login'))

def register(request):

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            #return render(request, 'users/login.html')
            return HttpResponseRedirect(reverse('users:login'))

    else:
        form = RegisterUserForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data['password']):
                request.user.delete()
                logout(request)
                return redirect('home')
            else:
                form.add_error('password', 'Неверный пароль')
    else:
        form = PasswordForm()

    return render(request, 'users/delete_account.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()

            # Обновляем сессию, чтобы пользователь не разлогинился
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Ваш пароль был успешно изменен')
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})

