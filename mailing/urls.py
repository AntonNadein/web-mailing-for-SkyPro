from django.urls import path

from mailing.apps import MailingConfig

from . import views

app_name = MailingConfig.name

urlpatterns = [
    path("", views.ListIndex.as_view(), name="home_page"),
    path("list_recipient/", views.MailingRecipientView.as_view(), name="recipient_list"),
    path("list_messages/", views.MessageView.as_view(), name="messages_list"),
    path("list_newsletter/", views.NewsletterView.as_view(), name="newsletter_list"),

    path("recipient/create/", views.MailingRecipientCreateView.as_view(), name="recipient_create"),
    path("message/create/", views.MessageCreateView.as_view(), name="message_create"),
    path("newsletter/create/", views.NewsletterCreateView.as_view(), name="newsletter_create"),

    path("recipient/detail/<slug:slug>/", views.MailingRecipientDetailView.as_view(), name="recipient_detail"),
    path("message/detail/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),
    path("newsletter/detail/<int:pk>/", views.NewsletterDetailView.as_view(), name="newsletter_detail"),

    path("recipient/update/<slug:slug>/", views.MailingRecipientUpdateView.as_view(), name="recipient_update"),
    path("message/update/<int:pk>/", views.MessageUpdateView.as_view(), name="message_update"),
    path("newsletter/update/<int:pk>/", views.NewsletterUpdateView.as_view(), name="newsletter_update"),

    path("recipient/delete/<slug:slug>/", views.MailingRecipientDeleteView.as_view(), name="recipient_delete"),
    path("message/delete/<int:pk>/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("newsletter/delete/<int:pk>/", views.NewsletterDeleteView.as_view(), name="newsletter_delete"),

    path("list_newsletter/moderation/", views.ModerationNewsletterView.as_view(), name="moderation_newsletter_list"),
    path("list_recipient/moderation/", views.ModerationMailingRecipientView.as_view(), name="moderation_recipient_list"),
    path("list_users/moderation/", views.ModerationUsersView.as_view(), name="moderation_user_list"),
    path("newsletter/moderation/<int:pk>/block/", views.ModerationNewsletterView.as_view(), name="moderation"),
    path('users/moderation/<int:pk>/block/', views.ModerationUsersView.as_view(), name='block_user'),
]
