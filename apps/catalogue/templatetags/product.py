from django import template
import json

register = template.Library()


@register.simple_tag(name='intersection_attribute')
def intersection_attribute(product_versions, attribute_values):
    return set(attribute.pk for attribute in product_versions.attributes.all()) & set(attribute_values)


register.filter('json', json.dumps)
