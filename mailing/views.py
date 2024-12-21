import datetime

from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import MailingRecipientForm, MessageForm, NewsletterForm
from .models import AttemptToSend, MailingRecipient, Message, Newsletter

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


class ListIndex(ListView):
    """Главная страница"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.count_newsletter(context)
        print(result)
        context["count_status"] = result[0]
        context["count_newsletter"] = result[1]
        context["unique_users"] = result[2]

        return context

    def count_newsletter(self, context):
        count_status = 0
        count_newsletter = 0
        user_list = []
        for i in context["newsletter"]:
            count_newsletter += 1
            if i.status == "started":
                count_status += 1
            users = i.recipients.all()
            for user in users:
                user_list.append(user)
        unique_users = len(set(user_list))
        return count_status, count_newsletter, unique_users


class MailingRecipientView(ListView):
    """Получатель рассылки"""

    model = MailingRecipient
    context_object_name = "recipients"
    template_name = "mailing/list_recipient.html"


class MessageView(ListView):
    """Сообщение"""

    model = Message
    context_object_name = "messages"
    template_name = "mailing/list_message.html"


class NewsletterView(ListView):
    """Рассылка"""

    model = Newsletter
    context_object_name = "newsletter"
    template_name = "mailing/list_newsletter.html"


class MailingRecipientCreateView(CreateView):
    """Получатель рассылки, создание"""

    model = MailingRecipient
    template_name = "mailing/create_recipient.html"
    form_class = MailingRecipientForm
    success_url = reverse_lazy("mailing:recipient_list")


class MessageCreateView(CreateView):
    """Сообщение, создание"""

    model = Message
    template_name = "mailing/create_message.html"
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class NewsletterCreateView(CreateView):
    """Рассылка, создание"""

    model = Newsletter
    template_name = "mailing/create_newsletter.html"
    form_class = NewsletterForm
    success_url = reverse_lazy("mailing:newsletter_list")


class MailingRecipientDetailView(DetailView):
    """Получатель рассылки, детали"""

    model = MailingRecipient
    context_object_name = "recipients"
    template_name = "mailing/detail_recipient.html"


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
        # получение и изменение данных рассылки
        newsletter = self.get_object()
        newsletter.status = "started"
        newsletter.first_dispatch = datetime.datetime.now()
        newsletter.save()

        # создаем экземпляр для регистрации попыток рассылок в БД
        attempt = AttemptToSend(attempts=datetime.datetime.now(), status=False, newsletter=newsletter)

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


class MailingRecipientUpdateView(UpdateView):
    """Получатель рассылки, обновление"""

    model = MailingRecipient
    template_name = "mailing/create_recipient.html"
    form_class = MailingRecipientForm
    success_url = reverse_lazy("mailing:recipient_list")


class MessageUpdateView(UpdateView):
    """Сообщение, обновление"""

    model = Message
    template_name = "mailing/create_message.html"
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class NewsletterUpdateView(UpdateView):
    """Рассылка, обновление"""

    model = Newsletter
    template_name = "mailing/create_newsletter.html"
    form_class = NewsletterForm
    success_url = reverse_lazy("mailing:newsletter_list")


class MailingRecipientDeleteView(DeleteView):
    """Получатель рассылки, удаление"""

    model = MailingRecipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


class MessageDeleteView(DeleteView):
    """Сообщение, удаление"""

    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:messages_list")


class NewsletterDeleteView(DeleteView):
    """Рассылка, удаление"""

    model = Newsletter
    template_name = "mailing/newsletter_confirm_delete.html"
    success_url = reverse_lazy("mailing:newsletter_list")
