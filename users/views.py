from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from asgiref.sync import sync_to_async


# Create your views here.

class MyLoginView(View):

    async def get(self, request):
        is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()

        if is_authenticated:
            return redirect('profile')

        form = await sync_to_async(AuthenticationForm)()
        return await sync_to_async(render)(request, 'users/login.html', {'form': form})

    async def post(self, request):
        form = await sync_to_async(lambda: AuthenticationForm(request, data=request.POST))()
        is_valid = await sync_to_async(form.is_valid)()

        if is_valid:
            user = await sync_to_async(lambda: form.get_user())()
            await sync_to_async(login)(request, user)
            return redirect('profile')
        else:
            await sync_to_async(messages.error)(request, 'Непарвильний логін або пароль')
            return await sync_to_async(render)(request, 'users/login.html', {'form': form})


class RegisterView(View):

    async def get(self, request):
        form = await sync_to_async(UserCreationForm)()
        return await sync_to_async(render)(request, 'users/register.html', {'form': form})

    async def post(self, request):
        form = await sync_to_async(lambda: UserCreationForm(request.POST))()
        is_valid = await sync_to_async(form.is_valid)()

        if is_valid:
            user = await sync_to_async(form.save)()
            await sync_to_async(login)(request, user)
            return redirect('home')
        else:
            await sync_to_async(messages.error)(request, 'Помилка реєстрації. Будь ласка, перевірте введені дані.')
            return await sync_to_async(render)(request, 'users/register.html', {'form': form})


class ProfileView(View):

    async def get(self, request):
        is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()

        if not is_authenticated:
            return redirect('login')

        return redirect('home')


class LogoutView(View):

    async def get(self, request):
        await sync_to_async(logout)(request)
        return redirect('login')
