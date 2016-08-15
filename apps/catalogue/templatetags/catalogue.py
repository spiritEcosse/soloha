from django.core.urlresolvers import reverse
from django.template import Library
register = Library()


@register.simple_tag
def reverse_url(app, url_extra_kwargs, **kwargs):
    dict_kwargs = url_extra_kwargs.copy()
    dict_kwargs.update(kwargs)
    return reverse(app, kwargs=dict_kwargs)
