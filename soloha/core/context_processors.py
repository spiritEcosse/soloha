__author__ = 'igor'

from apps.catalogue.models import Category
from apps.catalogue.models import Info
from soloha.settings import MAX_COUNT_CATEGORIES
from django.contrib.sites.shortcuts import get_current_site


def context_data(request):
    # queryset = SiteInfo.objects.get(domain=get_current_site(request).domain)
    return {
        'categories': Category.objects.filter(enable=True, level=0).select_related(
            'parent__parent'
        ).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES],
        # 'work_time': queryset.work_time,
        # 'address': queryset.address,
        # 'phone_number': queryset.phone_number,
        # 'email': queryset.email
    }

