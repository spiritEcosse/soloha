import logging
from apps.catalogue.models import Category
from apps.subscribe.forms import SubscribeForm
from soloha.settings import MAX_COUNT_CATEGORIES
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)
ANSWER = str(_('Subscribed successfully!'))


def context_data(request):
    context = dict()
    context['categories'] = Category.objects.filter(enable=True, level=0).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
    context['form'] = SubscribeForm()
    context['answer'] = ANSWER
    return context
