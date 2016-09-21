import logging
from apps.catalogue.models import Category
from apps.ex_flatpages.models import FlatPage
from apps.subscribe.forms import SubscribeForm
from soloha.settings import MAX_COUNT_CATEGORIES
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

logger = logging.getLogger(__name__)
ANSWER = str(_('Subscribed successfully!'))


def context_data(request):
    current_site = get_current_site(request)

    context = dict()
    queryset_info_page = FlatPage.objects.filter(sites__domain=get_current_site(request).domain)
    context['info_pages'] = queryset_info_page
    context['categories'] = Category.objects.filter(enable=True, level=0).select_related(
        'parent__parent'
    ).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
    context['contacts'] = '/contacts/'
    context['current_site'] = get_current_site(request)
    context['form'] = SubscribeForm()
    context['answer'] = ANSWER
    context['shop_tagline'] = current_site.info.shop_short_desc or settings.OSCAR_SHOP_TAGLINE
    context['shop_name'] = current_site.name
    return context
