from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView


class ProductCategoryView(CoreProductCategoryView):
    template_name = 'catalogue/soloha_category.html'
