from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.context_processors import messages
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView


# Create your views here.

class MyLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile')

    def form_invalid(self, form):
        messages.error(self.request, 'Непарвильний логін або пароль')
        return super().form_invalid(form)


class RegisterView(CreateView):
    # form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('profile')

    def get_success_url(self):
        return reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, form.instance)
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Помилка реєстрації. Будь ласка, перевірте введені дані.')
        return super().form_invalid(form)


class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        context = {
            'user': request.user
        }
        return render(request, 'users/profile.html', context)