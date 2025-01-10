from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.mixins import CachedViewMixin
from mailing.models import AttemptToSend


class IndexCounter:
    """Статистка главной страницы"""

    @staticmethod
    def count_attempt_to_send(user):
        """Статистика рассылок и количество успешных сообщений"""
        attempts = AttemptToSend.objects.filter(owner=user)
        count_attempt_successful = 0
        count_attempt_fail = 0
        count_message = 0
        for attempt in attempts:
            if attempt.status:
                count_attempt_successful += 1
                for recipient in attempt.newsletter.recipients.all():
                    count_message += 1
            else:
                count_attempt_fail += 1
        return count_attempt_successful, count_attempt_fail, count_message

    @staticmethod
    def count_newsletter(context):
        """Подсчет рассылок и уникальных получателей"""
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


class CachedListView(LoginRequiredMixin, CachedViewMixin, ListView):
    """Класс для представлений ListView с кэшированным queryset"""

    def get_queryset(self):
        """Получает queryset, пытаясь использовать кэш."""
        queryset = self.get_cached_queryset()
        if queryset is not None:
            return queryset

        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(owner=user)  # queryset конкретного пользователя
        self.cache_queryset(queryset)

        return queryset


class CachedCreateView(LoginRequiredMixin, CachedViewMixin, CreateView):
    """Класс для представлений CreateView с кэшированным queryset"""

    def form_valid(self, form):
        """Сохраняем форму конкретного пользователя и обновляем кэш"""
        data = form.save()
        user = self.request.user
        data.owner = user
        data.save()

        queryset = self.get_queryset()
        user = self.request.user
        queryset = queryset.filter(owner=user)
        self.cache_queryset(queryset)
        return super().form_valid(form)


class CachedUpdateView(CachedCreateView, CachedViewMixin, UpdateView):
    """Класс для представлений UpdateView с кэшированным queryset"""

    def form_valid(self, form):
        response = super().form_valid(form)

        queryset = self.get_queryset()
        user = self.request.user
        queryset = queryset.filter(owner=user)
        self.cache_queryset(queryset)
        return response


class CachedDeleteView(LoginRequiredMixin, CachedViewMixin, DeleteView):
    """Класс для представлений UpdateView с кэшированным queryset"""

    def form_valid(self, form):

        success_url = self.get_success_url()
        self.object.delete()

        queryset = self.get_queryset()
        user = self.request.user
        queryset = queryset.filter(owner=user)
        self.cache_queryset(queryset)
        return HttpResponseRedirect(success_url)
