from django.contrib import admin

from mailing.models import AttemptToSend, MailingRecipient, Message, Newsletter


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    """Получатель рассылки"""

    list_display = (
        "id",
        "first_name",
        "last_name",
        "patronymic",
        "email",
        "slug",
        "comment",
    )
    list_filter = (
        "last_name",
        "first_name",
    )
    search_fields = ("last_name",)
    ordering = ("last_name",)
    prepopulated_fields = {"slug": ["first_name", "last_name"]}
    fields = [
        ("last_name", "first_name"),
        ("patronymic", "slug"),
        "email",
        "comment",
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Сообщение"""

    list_display = (
        "id",
        "title",
        "body_message",
    )
    list_filter = ("title",)
    search_fields = ("title",)
    ordering = ("title",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Рассылка"""

    list_display = (
        "id",
        "name",
        "text",
        "status",
        "first_dispatch",
        "end_dispatch",
    )
    list_filter = (
        "name",
        "status",
    )
    ordering = (
        "status",
        "name",
    )
    filter_horizontal = ("recipients",)
    fields = [("name", "status"), "text", "recipients", ("first_dispatch", "end_dispatch")]


@admin.register(AttemptToSend)
class AttemptToSendAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "attempts",
        "status",
        "server_response",
        "newsletter",
    )
    list_filter = ("status",)
    ordering = ("status",)
