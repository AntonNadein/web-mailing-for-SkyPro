import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView

from users.models import ModelUser

from .forms import MailingRecipientForm, MessageForm, NewsletterForm
from .mixins import CachedViewMixin
from .models import AttemptToSend, MailingRecipient, Message, Newsletter
from .services import CachedCreateView, CachedDeleteView, CachedListView, CachedUpdateView, IndexCounter

menu = [
    {
        "title": "Получатель рассылки",
        "list": "Список получателей",
        "create": "Создать",
        "update": "Обновить данные",
        "delete": "Удалить",
        "unique": "unic1",
        "url": "mailing:recipient_list",
        "url_create": "mailing:recipient_create",
    },
    {
        "title": "Управление сообщениями",
        "list": "Список сообщенй",
        "create": "Создать",
        "update": "Обновить данные",
        "delete": "Удалить",
        "unique": "unic2",
        "url": "mailing:messages_list",
        "url_create": "mailing:message_create",
    },
    {
        "title": "Управление рассылками",
        "list": "Список рассылок",
        "create": "Создать",
        "update": "Обновить данные",
        "delete": "Удалить",
        "unique": "unic3",
        "url": "mailing:newsletter_list",
        "url_create": "mailing:newsletter_create",
    },
]


class ModerationMailingRecipientView(LoginRequiredMixin, PermissionRequiredMixin, CachedViewMixin, ListView):
    """Просмотр всех клиентов менеджером"""

    model = MailingRecipient
    context_object_name = "recipients"
    template_name = "mailing/moderation/list_recipient.html"
    permission_required = "mailing.view_all_mailing_recipient"

    def get_queryset(self):
        """Получает queryset, пытаясь использовать кэш."""
        queryset = self.get_cached_queryset()
        if queryset is not None:
            return queryset

        queryset = super().get_queryset()
        self.cache_queryset(queryset)
        return queryset


class ModerationNewsletterView(LoginRequiredMixin, PermissionRequiredMixin, CachedViewMixin, ListView):
    """Просмотр всех рассылок менеджером"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/moderation/list_newsletter.html"
    permission_required = "mailing.view_all_newsletter"

    def get_queryset(self):
        """Получает queryset, пытаясь использовать кэш."""
        queryset = self.get_cached_queryset()
        if queryset is not None:
            return queryset

        queryset = super().get_queryset()
        self.cache_queryset(queryset)
        return queryset

    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, id=pk)

        if not request.user.has_perm("mailing.disabling_mailings"):
            return HttpResponseForbidden("У вас нет прав для отключения рассылки.")

        newsletter.is_active = False
        newsletter.save()

        messages.success(request, f"Рассылка {newsletter} успешно отключена.")

        return redirect("mailing:newsletter_detail", pk=pk)


class ModerationUsersView(LoginRequiredMixin, PermissionRequiredMixin, CachedViewMixin, ListView):
    """Просмотр списка пользователей сервиса"""

    model = ModelUser
    context_object_name = "users"
    template_name = "mailing/moderation/list_users.html"
    permission_required = "users.can_block_user"

    def get_queryset(self):
        """Получает queryset, пытаясь использовать кэш."""
        queryset = self.get_cached_queryset()
        if queryset is not None:
            return queryset

        queryset = super().get_queryset()
        queryset = queryset.filter(groups__name="Пользователь")
        self.cache_queryset(queryset)

        return queryset

    def post(self, request, pk):
        user = get_object_or_404(ModelUser, id=pk)

        if not request.user.has_perm("users.can_block_user"):
            return HttpResponseForbidden("У вас нет прав для блокировки пользователей.")

        user.is_active = False
        user.save()

        messages.success(request, f"Пользователь {user.username} успешно заблокирован.")

        return redirect("mailing:moderation_user_list")


class ListIndex(ListView):
    """Главная страница"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/index.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            user = self.request.user
            return queryset.filter(owner=user)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        result = IndexCounter.count_newsletter(context)
        context["count_status"] = result[0]
        context["count_newsletter"] = result[1]
        context["unique_users"] = result[2]

        if self.request.user.is_authenticated:
            result_2 = IndexCounter.count_attempt_to_send(self.request.user)
            context["count_attempt_successful"] = result_2[0]
            context["count_attempt_fail"] = result_2[1]
            context["count_message"] = result_2[2]

        return context


class MailingRecipientView(CachedListView):
    """Получатель рассылки"""

    model = MailingRecipient
    context_object_name = "recipients"
    template_name = "mailing/list_recipient.html"


class MessageView(CachedListView):
    """Сообщение"""

    model = Message
    context_object_name = "messages"
    template_name = "mailing/list_message.html"


class NewsletterView(CachedListView):
    """Рассылка"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/list_newsletter.html"


class MailingRecipientCreateView(CachedCreateView):
    """Получатель рассылки, создание"""

    model = MailingRecipient
    template_name = "mailing/create_recipient.html"
    form_class = MailingRecipientForm
    success_url = reverse_lazy("mailing:recipient_list")


class MessageCreateView(CachedCreateView):
    """Сообщение, создание"""

    model = Message
    template_name = "mailing/create_message.html"
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class NewsletterCreateView(CachedCreateView):
    """Рассылка, создание"""

    model = Newsletter
    template_name = "mailing/create_newsletter.html"
    form_class = NewsletterForm
    success_url = reverse_lazy("mailing:newsletter_list")

    def get_form_kwargs(self):
        """Добавляем текущего пользователя в kwargs для формы"""

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingRecipientDetailView(DetailView):
    """Получатель рассылки, детали"""

    model = MailingRecipient
    context_object_name = "recipients"
    template_name = "mailing/detail_recipient.html"


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDetailView(DetailView):
    """Сообщение, детали"""

    model = Message
    context_object_name = "messages"
    template_name = "mailing/detail_message.html"


class NewsletterDetailView(DetailView):
    """Рассылка, детали"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/detail_newsletter.html"

    def post(self, request, *args, **kwargs):
        """Получение и изменение данных рассылки"""

        newsletter = self.get_object()
        newsletter.status = "started"
        newsletter.first_dispatch = datetime.datetime.now()
        newsletter.save()

        # создаем экземпляр для регистрации попыток рассылок в БД
        owner = newsletter.owner
        attempt = AttemptToSend(attempts=datetime.datetime.now(), status=False, newsletter=newsletter, owner=owner)

        # логика отправки сообщения
        try:
            self.send_newsletter(newsletter)
            newsletter.status = "completed"
            newsletter.end_dispatch = datetime.datetime.now()
            attempt.status = True
            attempt.server_response = "Рассылка успешно отправлена"
            messages.success(request, "Рассылка успешно отправлена.")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке рассылки: {str(e)}")
            attempt.server_response = str(e)

        attempt.save()
        newsletter.save()
        return HttpResponseRedirect(reverse_lazy("mailing:newsletter_detail", args=[newsletter.id]))

    def send_newsletter(self, newsletter):
        """Метод для отправки сообщений newsletter."""
        recipients = newsletter.recipients.all()

        for recipient in recipients:
            self.send_emails(recipient.email, newsletter.text.title, newsletter.text.body_message)

    def send_emails(self, emails, subject, message):
        """Функция отправки email-сообщений."""

        send_mail(
            subject,
            message,
            from_email=None,
            recipient_list=[emails],
            fail_silently=False,
        )


class MailingRecipientUpdateView(PermissionRequiredMixin, CachedUpdateView):
    """Получатель рассылки, обновление"""

    model = MailingRecipient
    template_name = "mailing/create_recipient.html"
    form_class = MailingRecipientForm
    permission_required = "mailing.change_mailingrecipient"
    success_url = reverse_lazy("mailing:recipient_list")


class MessageUpdateView(PermissionRequiredMixin, CachedUpdateView):
    """Сообщение, обновление"""

    model = Message
    template_name = "mailing/create_message.html"
    form_class = MessageForm
    permission_required = "mailing.change_message"
    success_url = reverse_lazy("mailing:messages_list")


class NewsletterUpdateView(PermissionRequiredMixin, CachedUpdateView):
    """Рассылка, обновление"""

    model = Newsletter
    template_name = "mailing/create_newsletter.html"
    form_class = NewsletterForm
    permission_required = "mailing.change_newsletter"
    success_url = reverse_lazy("mailing:newsletter_list")


class MailingRecipientDeleteView(PermissionRequiredMixin, CachedDeleteView):
    """Получатель рассылки, удаление"""

    model = MailingRecipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")
    permission_required = "mailing.delete_message"


class MessageDeleteView(PermissionRequiredMixin, CachedDeleteView):
    """Сообщение, удаление"""

    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:messages_list")
    permission_required = "mailing.delete_mailingrecipient"


class NewsletterDeleteView(PermissionRequiredMixin, CachedDeleteView):
    """Рассылка, удаление"""

    model = Newsletter
    template_name = "mailing/newsletter_confirm_delete.html"
    success_url = reverse_lazy("mailing:newsletter_list")
    permission_required = "mailing.delete_newsletter"
