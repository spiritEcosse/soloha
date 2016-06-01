from oscar.apps.promotions.app import PromotionsApplication as CorePromotionsApplication
from django.conf.urls import url
from apps.promotions.views import HitsView, SpecialView, RecommendView, NewView, CategoriesView
from django.conf.urls.static import static
from soloha import settings


class PromotionsApplication(CorePromotionsApplication):
    hits_view = HitsView
    special_view = SpecialView
    recommend_view = RecommendView
    new_view = NewView
    categories = CategoriesView

    def get_urls(self):
        urls = super(PromotionsApplication, self).get_urls()
        urls += [
            url(r'^hits/', self.hits_view.as_view(), name='hits'),
            url(r'^special/', self.special_view.as_view(), name='special'),
            url(r'^recommend/', self.recommend_view.as_view(), name='recommend'),
            url(r'^new/', self.new_view.as_view(), name='new'),
            url(r'^categories/', self.categories.as_view(), name='categories'),
        ]
        return urls

application = PromotionsApplication()
