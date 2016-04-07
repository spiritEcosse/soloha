from django import template

register = template.Library()


@register.filter(name='concatenate')
def subtraction(category, filter_slugs, filter):
    category_absolute_url = category.get_absolute_url()
    filter_slug = filter.get_absolute_url()
    if filter_slugs:
        return category_absolute_url
    filter_slugs = filter_slugs.split('/')
    if filter_slug in filter_slugs:
        filter_slugs.remove(filter_slug)
    filter_slugs = '/'.join(filter_slugs)
    absolute_url = category.get_absolute_url({'filter_slug': filter_slugs})
    return absolute_url
    # return "{0}/filter/{1}/".format(category_absolute_url, filter_slugs)

@register.filter(name='subtraction')
def concatenate(category, filter_slugs, filter):
    category_absolute_url = category.get_absolute_url()
    filter_slug = filter.get_absolute_url()
    if filter_slugs:
        filter_slugs = filter_slugs.split('/')
    else:
        return category.get_absolute_url({'filter_slug': ''})
    filter_slugs.append(filter_slug)
    filter_slugs = '/'.join(filter_slugs)
    absolute_url = category.get_absolute_url({'filter_slug': filter_slugs})
    return absolute_url
    # return "{0}/filter/{1}".format(category_absolute_url, filter_slugs)

