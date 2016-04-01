__author__ = 'igor'

from apps.catalogue.models import Category
from soloha.settings import MAX_COUNT_CATEGORIES


def context_data(request):
    return {
        'categories': Category.objects.filter(enable=True, level=0).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
    }
