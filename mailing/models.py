from django.db import models


class MailingRecipient(models.Model):
    """Получатель рассылки"""

    first_name = models.CharField(max_length=250, verbose_name="Имя")
    last_name = models.CharField(max_length=250, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=250, verbose_name="Отчество")
    email = models.EmailField(unique=True, verbose_name="Email")
    comment = models.TextField(null=True, blank=True, verbose_name="Коментарий")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="URL",
        help_text="Уникальное имя формируется из фамилии и имени",
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    # def get_absolute_url(self):
    #     return reverse("mailing:mailing_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "получателя рассылки"
        verbose_name_plural = "Получатель рассылки"
        ordering = ["last_name"]


class Message(models.Model):
    """Сообщение"""

    title = models.CharField(max_length=250, verbose_name="Тема письма")
    body_message = models.TextField(verbose_name="Тело письма")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "Сообщение"


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
    first_dispatch = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время первой отправки")
    end_dispatch = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания отправки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "рассылку"
        verbose_name_plural = "Рассылка"


class AttemptToSend(models.Model):
    """Попытка рассылки"""

    SUCCESSFULLY = True
    NOT_SUCCESSFULLY = False

    STATUS = [(SUCCESSFULLY, "Успешно"), (NOT_SUCCESSFULLY, "Не успешно")]
    name = models.CharField(max_length=150, verbose_name="Название")
    attempts = models.DateTimeField(verbose_name="Дата и время попытки")
    status = models.BooleanField(choices=STATUS, verbose_name="Статус")
    server_response = models.TextField(verbose_name="Ответ почтового сервера")
    newsletter = models.ForeignKey(
        "Newsletter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletter",
        verbose_name="Рассылка",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "попытки рассылок"
        verbose_name_plural = "Попытка рассылки"
