from django.contrib.sites.models import Site
from soloha.settings import SITE_ID
from django.db.models import Prefetch
from apps.ex_sites.models import PhoneNumber


def context_data(request):
    context = {}
    site = Site.objects.filter(pk=SITE_ID).select_related('info').prefetch_related(
        Prefetch('info__phone_numbers', queryset=PhoneNumber.objects.browse()),
    ).get()
    context['current_site'] = site
    print site.info.phone_numbers.all()

    flatpages = site.flatpage_set.select_related('info').filter(info__position__in=('header', 'footer')).only(
        'url',
        'title',
        'info__icon',
        'info__position',
    ).order_by()
    key = lambda flatpage: 'flatpages_{}'.format(flatpage.info.position)

    for flatpage in flatpages:
        key_flatpage = key(flatpage)

        if key_flatpage not in context:
            context[key_flatpage] = []

        context[key_flatpage].append(flatpage)

    return context
