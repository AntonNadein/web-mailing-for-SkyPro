from django.urls import path

from mailing.apps import MailingConfig

from . import views

app_name = MailingConfig.name

urlpatterns = [
    path("", views.index, name="home_page"),
]
