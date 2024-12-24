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
