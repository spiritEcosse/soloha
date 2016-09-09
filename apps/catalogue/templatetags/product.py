from django import template
from soloha import settings

register = template.Library()


@register.simple_tag(name='intersection_attribute')
def intersection_attribute(product_versions, attribute_values):
    return set(attribute.pk for attribute in product_versions.attributes.all()) & set(attribute_values)


@register.inclusion_tag('catalogue/partials/recommended_products.html')
def recommended_products(product):
    """
    Inclusion tag listing recommended products
    """
    return {'recommended_products': product.recommended_products.all()[:settings.RECOMMENDED_PRODUCTS]}


@register.filter
def join_list(list, separator):
    return separator.join(list)


@register.filter
def join_slug(list, separator):
    return separator.join([item.slug for item in list])


@register.filter
def split(str, splitter):
    if str:
        return str.split(splitter)
    return []
