from django.core.urlresolvers import reverse
from django.template import Library
from django import template
register = Library()


@register.simple_tag
def reverse_url(app, url_extra_kwargs, **kwargs):
    dict_kwargs = url_extra_kwargs.copy()

    for key, value in kwargs.items():
        if value is None:
            dict_kwargs.pop(key, None)
            del kwargs[key]

    dict_kwargs.update(kwargs)
    return reverse(app, kwargs=dict_kwargs)


class AssignNode(template.Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''


def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.

    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}

    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)


register.tag('assign', do_assign)
