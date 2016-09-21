from oscar.apps.basket.app import BasketApplication as CoreBasketApplication
from django.conf.urls import url
from apps.basket.views import BasketAddWithAttributesView


class BasketApplication(CoreBasketApplication):
    add_view_with_attributes = BasketAddWithAttributesView

    def get_urls(self):
        urls = super(BasketApplication, self).get_urls()

        urls += [
            url(
                r'^add_with_attributes/(?P<pk>\d+)/$', self.add_view_with_attributes.as_view(),
                name='add_with_attributes'
            ),
        ]
        return self.post_process_urls(urls)

application = BasketApplication()
