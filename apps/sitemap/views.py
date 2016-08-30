from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from oscar.core.loading import get_model
from django.contrib.sites.shortcuts import get_current_site
from apps.flatpages.models import FlatPage

Category = get_model('catalogue', 'category')


class SitemapView(generic.ListView):
    template_name = 'sitemap/sitemap.html'
    model = Category

    def get_context_data(self, **kwargs):
        context = super(SitemapView, self).get_context_data(**kwargs)
        context['info_page'] = self.get_info_page()
        context['contacts'] = {'title': 'Contact us', 'url': '/contacts/'}
        return context

    def get_queryset(self):
        queryset = super(SitemapView, self).get_queryset()
        return queryset

    def get_info_page(self):
        queryset = FlatPage.objects.filter(sites__name=get_current_site(self.request).domain)
        return queryset

