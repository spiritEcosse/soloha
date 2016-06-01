from django import template

register = template.Library()


@register.simple_tag(name='concatenate')
def concatenate(category, filter_slugs, filter):
    if filter_slugs:
        filter_slugs = filter_slugs.split('/')
    else:
        filter_slugs = []
    if filter.get_absolute_url() in filter_slugs:
        filter_slugs.remove(filter.get_absolute_url())
    else:
        filter_slugs.append(filter.get_absolute_url())
    filter_slugs = '/'.join((filter_slugs))
    return category.get_absolute_url({'filter_slug': filter_slugs})