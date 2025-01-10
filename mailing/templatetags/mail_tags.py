from django import template
from django.urls import reverse

from mailing.views import menu

register = template.Library()


@register.inclusion_tag("mailing/tags/menu.html")
def show_menu(request):
    for item in menu:
        item["full_url"] = reverse(item["url"])
        item["u_create"] = reverse(item["url_create"])
    is_manager = request.user.groups.filter(name="Менеджер").exists()
    return {"menu": menu, "user": request.user, "is_manager": is_manager}
