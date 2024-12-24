from django import forms

from transliterate import translit

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'slug' not in self.initial:
            self.fields['slug'].initial = 'default-slug'

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        slug = cleaned_data.get('slug')

        if first_name and last_name and 'default-slug' in slug:
            generated_slug = f"{first_name}-{last_name}"
            cleaned_data['slug'] = translit(generated_slug.lower(), 'ru', reversed=True)

        return cleaned_data


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
        ]

    def __init__(self, *args, **kwargs):
        # делаем фильтрацию форм для авторизованных пользователей
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user is not None:
            self.fields['text'].queryset = Message.objects.filter(owner=self.user)
            self.fields['recipients'].queryset = MailingRecipient.objects.filter(owner=self.user)
