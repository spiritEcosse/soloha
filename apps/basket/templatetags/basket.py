import re
from django.template import Library, Node, Variable, TemplateSyntaxError
from widget_tweaks.templatetags.widget_tweaks import FieldAttributeNode
from django.template.debug import DebugParser
from django import template
from oscar.core.loading import get_model
from oscar.core.loading import get_class

AddToBasketForm = get_class('basket.forms', 'AddToBasketForm')
SimpleAddToBasketForm = get_class('basket.forms', 'SimpleAddToBasketForm')
Product = get_model('catalogue', 'product')
QNT_SINGLE, QNT_MULTIPLE = 'single', 'multiple'
parser = DebugParser

register = template.Library()

ATTRIBUTE_RE = re.compile(r"""
    (?P<attr>
        [\w_-]+
    )
    (?P<sign>
        \+?=
    )
    (?P<value>
    ['"]? # start quote
        [^"']*
    ['"]? # end quote
    )
""", re.VERBOSE | re.UNICODE)


@register.simple_tag
def basket_render_field(*args, **kwargs):
    """
    Render a form field using given attribute-value pairs

    Takes form field as first argument and list of attribute-value pairs for
    all other arguments.  Attribute-value pairs should be in the form of
    attribute=value or attribute="a value" for assignment and attribute+=value
    or attribute+="value" for appending.
    """
    # error_msg = '%r tag requires a form field followed by a list of attributes and values in the form attr="value"' % token.split_contents()[0]
    form_field = parser.compile_filter(form_field)

    set_attrs = []
    append_attrs = []
    for pair in kwargs.items():
        match = ATTRIBUTE_RE.match(pair)
        if not match:
            raise TemplateSyntaxError(error_msg + ": %s" % pair)
        dct = match.groupdict()
        attr, sign, value = dct['attr'], dct['sign'], parser.compile_filter(dct['value'])

        if sign == "=":
            set_attrs.append((attr, value))
        else:
            append_attrs.append((attr, value))

    return FieldAttributeNode(form_field, set_attrs, append_attrs)


@register.assignment_tag()
def basket_form(request, product, quantity_type='single'):
    if not isinstance(product, Product):
        return ''

    initial = {}
    if not product.is_parent:
        initial['product_id'] = product.id

    form_class = AddToBasketForm
    if quantity_type == QNT_SINGLE:
        form_class = SimpleAddToBasketForm

    form = form_class(request.basket, product=product, initial=initial)

    return form
