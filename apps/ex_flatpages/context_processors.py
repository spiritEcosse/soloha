from django.contrib.flatpages.models import FlatPage
from apps.ex_flatpages.models import InfoPage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.db.models import Prefetch


def context_data(request):
    current_site = get_current_site(request)

    flatpages = Site.objects.filter(pk=current_site.pk).prefetch_related(
        Prefetch(
            'flatpage_set',
            queryset=FlatPage.objects.filter(
                info__position=InfoPage.FOOTER
            ), to_attr='flatpages_footer'
        ),
        Prefetch(
            'flatpage_set',
            queryset=FlatPage.objects.filter(
                info__position=InfoPage.HEADER
            ), to_attr='flatpages_header'
        )
    )
    return {'current_site': flatpages.first()}
