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

