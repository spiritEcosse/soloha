from django.core.urlresolvers import reverse
from django import template
from django.template import Node, Library, TemplateSyntaxError, VariableDoesNotExist, NodeList, resolve_variable
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


def do_ifinlist(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfInListNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)


def ifinlist(parser, token):
    """
    Given an item and a list, check if the item is in the list

    -----
    item = 'a'
    list = [1, 'b', 'a', 4]
    -----
    {% ifinlist item list %}
        Yup, it's in the list
    {% else %}
        Nope, it's not in the list
    {% endifinlist %}
    """
    return do_ifinlist(parser, token, False)
ifinlist = register.tag(ifinlist)


class IfInListNode(Node):
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = var1, var2
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfInListNode>"

    def render(self, context):
        try:
            val1 = resolve_variable(self.var1, context)
        except VariableDoesNotExist:
            val1 = None
        try:
            val2 = resolve_variable(self.var2, context)
        except VariableDoesNotExist:
            val2 = None
        if val1 in val2:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.filter
def in_list(needle, list):
    return needle in list


@register.filter
def remove(list, needle):
    copy = list[:]

    try:
        copy.remove(needle)
    except ValueError:
        pass

    return copy


@register.filter
def append(list, needle):
    copy = list[:]
    copy.append(needle)
    return copy
