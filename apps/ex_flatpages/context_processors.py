from django.contrib.sites.models import Site
from soloha.settings import SITE_ID


def context_data(request):
    context = {}
    site = Site.objects.filter(pk=SITE_ID).select_related('info').prefetch_related('info__phone_numbers').get()
    context['current_site'] = site
    flatpages = site.flatpage_set.select_related('info').filter(info__position__in=('header', 'footer'))
    key = lambda flatpage: 'flatpages_{}'.format(flatpage.info.position)
    [context.setdefault(key(flatpage), []).append(flatpage) for flatpage in flatpages]
    return context
