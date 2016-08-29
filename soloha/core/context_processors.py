import logging
from django.core.exceptions import ObjectDoesNotExist

from apps.catalogue.models import Category
from apps.ex_sites.models import Info
from apps.flatpages.models import InfoPage
from apps.subscribe.forms import SubscribeForm
from soloha.settings import MAX_COUNT_CATEGORIES
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from soloha.settings import CACHE_MIDDLEWARE_SECONDS, KEY_PREFIX
logger = logging.getLogger(__name__)
ANSWER = str(_('Subscribed successfully!'))


def context_data(request):
    key = KEY_PREFIX + 'context_processors'
    context = cache.get(key)

    if not context:
        context = dict()
        queryset_info_page = InfoPage.objects.filter(sites__domain=get_current_site(request).domain)
        context['info_pages'] = queryset_info_page
        context['categories'] = Category.objects.filter(enable=True, level=0).select_related(
            'parent__parent'
        ).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
        context['contacts'] = '/contacts/'
        context['current_site'] = get_current_site(request)
        context['form'] = SubscribeForm()
        context['answer'] = ANSWER
        cache.set(key, context, CACHE_MIDDLEWARE_SECONDS)

    return context
