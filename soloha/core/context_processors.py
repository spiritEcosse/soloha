__author__ = 'igor'


import logging
from django.core.exceptions import ObjectDoesNotExist

from apps.catalogue.models import Category
from apps.catalogue.models import SiteInfo
from apps.flatpages.models import InfoPage
from soloha.settings import MAX_COUNT_CATEGORIES
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger(__name__)


def context_data(request):
    context = dict()
    queryset_info_page = InfoPage.objects.filter(sites__name=get_current_site(request).domain)
    context['info_pages'] = queryset_info_page
    context['categories'] = Category.objects.filter(enable=True, level=0).select_related(
        'parent__parent'
    ).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
    context['contacts'] = '/contacts/'
    try:
        queryset = SiteInfo.objects.get(domain=get_current_site(request).domain)
    except ObjectDoesNotExist as msg:
        logger.warning(msg)
    else:
        context['work_time'] = queryset.work_time
        context['address'] = queryset.address
        context['phone_number'] = queryset.phone_number
        context['email'] = queryset.email

    return context


