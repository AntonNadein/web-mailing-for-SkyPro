from django.db import models
from django.urls import reverse

from users.models import ModelUser


class MailingRecipient(models.Model):
    """Получатель рассылки"""

    first_name = models.CharField(max_length=250, verbose_name="Имя")
    last_name = models.CharField(max_length=250, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=250, null=True, blank=True, verbose_name="Отчество")
    email = models.EmailField(unique=True, verbose_name="Email")
    comment = models.TextField(null=True, blank=True, verbose_name="Коментарий")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="URL",
        help_text="Уникальное имя формируется из фамилии и имени",
    )
    owner = models.ForeignKey(
        ModelUser, on_delete=models.CASCADE, null=True, blank=True, related_name="recipient", verbose_name="Владелец"
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def get_absolute_url(self):
        return reverse("mailing:recipient_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "получателя рассылки"
        verbose_name_plural = "Получатель рассылки"
        ordering = ["last_name"]
        permissions = [
            ("view_all_mailing_recipient", "View all mailing recipient"),
        ]


class Message(models.Model):
    """Сообщение"""

    title = models.CharField(max_length=250, verbose_name="Тема письма")
    body_message = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(
        ModelUser, on_delete=models.CASCADE, null=True, blank=True, related_name="message", verbose_name="Владелец"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "Сообщение"
        permissions = [
            ("view_all_message", "View all message"),
        ]


class Newsletter(models.Model):
    """Рассылка"""

    CREATED = "created"
    STARTED = "started"
    COMPLETED = "completed"

    STATUS = [(CREATED, "Создана"), (STARTED, "Запущена"), (COMPLETED, "Завершена")]

    name = models.CharField(max_length=150, verbose_name="Название рассылки")
    recipients = models.ManyToManyField("MailingRecipient", related_name="recipients", verbose_name="Получатели")
    text = models.ForeignKey(
        "Message",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_text",
        verbose_name="Сообщение",
    )
    status = models.CharField(max_length=15, choices=STATUS, verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Активность")
    owner = models.ForeignKey(
        ModelUser, on_delete=models.CASCADE, null=True, blank=True, related_name="newsletter", verbose_name="Владелец"
    )
    first_dispatch = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время первой отправки")
    end_dispatch = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания отправки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "рассылку"
        verbose_name_plural = "Рассылка"
        permissions = [
            ("view_all_newsletter", "View all newsletter"),
            ("disabling_mailings", "Disabling mailings"),
        ]

    @property
    def human_readable_status(self):
        return dict(self.STATUS).get(self.status, "Неизвестный статус")


class AttemptToSend(models.Model):
    """Попытка рассылки"""

    SUCCESSFULLY = True
    NOT_SUCCESSFULLY = False

    STATUS = [(SUCCESSFULLY, "Успешно"), (NOT_SUCCESSFULLY, "Не успешно")]

    attempts = models.DateTimeField(verbose_name="Дата и время попытки")
    status = models.BooleanField(choices=STATUS, verbose_name="Статус")
    server_response = models.TextField(verbose_name="Ответ почтового сервера")
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        ModelUser, on_delete=models.CASCADE, null=True, blank=True, related_name="attempt", verbose_name="Владелец"
    )

    def __str__(self):
        return f"Попытка от {self.attempts} - Статус: {'Успешно' if self.status else 'Не успешно'}"

    class Meta:
        verbose_name = "попытки рассылок"
        verbose_name_plural = "Попытка рассылки"
