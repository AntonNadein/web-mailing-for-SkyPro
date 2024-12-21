from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import CustomUserCreationForm, ProfileUserForm, UserAuthenticationForm
from users.models import ModelUser


class UserCreateView(CreateView):
    """Представление регистрации профиля"""

    model = ModelUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        self.send_welcome_mail(user.email)
        return super().form_valid(form)

    def send_welcome_mail(self, user_email):
        subject = "Добро пожаловать на наш сайт"
        message = "Спасибо, что зарегистрировались в нашем интернет магазине!"
        from_email = EMAIL_HOST_USER
        recipient_list = [
            user_email,
        ]
        send_mail(subject, message, from_email, recipient_list)


class UserLoginView(LoginView):
    """Представление авторизации"""

    form_class = UserAuthenticationForm
    template_name = "users/login.html"


class UserDetailView(DetailView):
    """Представление профиля"""

    model = ModelUser
    template_name = "users/profile.html"
    context_object_name = "user"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Представление редактирования профиля"""

    model = ModelUser
    form_class = ProfileUserForm
    template_name = "users/register.html"

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"pk": self.object.pk})