import datetime

from django.core.management.base import BaseCommand

from mailing.models import AttemptToSend, Newsletter
from mailing.views import NewsletterDetailView


class Command(BaseCommand, NewsletterDetailView):
    help = "Send newsletters to subscribers"

    def add_arguments(self, parser):
        parser.add_argument("newsletter_id", type=int)

    def handle(self, *args, **kwargs):
        newsletter_id = kwargs["newsletter_id"]
        newsletter = Newsletter.objects.get(id=newsletter_id)

        newsletter.status = "started"
        newsletter.first_dispatch = datetime.datetime.now()
        newsletter.save()

        attempt = AttemptToSend(attempts=datetime.datetime.now(), status=False, newsletter=newsletter)

        try:
            self.send_newsletter(newsletter)
            newsletter.status = "completed"
            newsletter.end_dispatch = datetime.datetime.now()
            attempt.status = True
            attempt.server_response = "Рассылка успешно отправлена"
        except Exception as e:
            attempt.server_response = str(e)
        attempt.save()
        newsletter.save()
