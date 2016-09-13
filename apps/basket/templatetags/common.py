from django import template

register = template.Library()


@register.filter
def join(list, separator):
    return separator.join([item.title for item in list])
