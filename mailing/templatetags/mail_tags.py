from django import template
from django.urls import reverse

from mailing.views import menu

register = template.Library()


@register.inclusion_tag("mailing/tags/menu.html")
def show_menu():
    for item in menu:
        item["full_url"] = reverse(item["url"])
        item["u_create"] = reverse(item["url_create"])
    return {"menu": menu}
