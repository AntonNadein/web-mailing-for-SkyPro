from django import forms

from mailing.models import MailingRecipient, Message, Newsletter


class MixinForms:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class MailingRecipientForm(MixinForms, forms.ModelForm):

    class Meta:
        model = MailingRecipient
        fields = [
            "last_name",
            "first_name",
            "patronymic",
            "slug",
            "email",
            "comment",
        ]


class MessageForm(MixinForms, forms.ModelForm):

    class Meta:
        model = Message
        fields = [
            "title",
            "body_message",
        ]


class NewsletterForm(MixinForms, forms.ModelForm):

    class Meta:
        model = Newsletter
        fields = [
            "name",
            "recipients",
            "text",
            "status",
            "first_dispatch",
            "end_dispatch",
        ]
