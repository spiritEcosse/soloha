from oscar.test import factories
from oscar.core.loading import get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs

ProductCategory = get_model('catalogue', 'productcategory')
Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class Test(object):
    @classmethod
    def create_category(cls):
        """
        create bulk category
        Returns:
            None
        """
        categories = (
            '1',
            '2 > 21',
            '2 > 22',
            '2 > 23 > 231',
            '2 > 24',
            '3',
            '4 > 41',
        )
        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)

    def create_product_bulk(self):
        """
        create bulk product with category and object image
        Returns:
            None
        """
        self.create_category()

        for num in xrange(1, 100):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)
            category = Category.objects.get(name='231')
            product_category = ProductCategory(product=product, category=category)
            product_category.save()
            category = Category.objects.get(name='41')
            product_category = ProductCategory(product=product, category=category)
            product_category.save()

    def create_product_bulk_recommend(self):
        """
        create product bulk with model ProductRecommendation
        Returns:
            None
        """
        self.create_product_bulk()
        product_desc = Product.objects.all().order_by('-date_created')
        product_asc = Product.objects.all().order_by('date_created')

        for num in xrange(0, len(product_desc)):
            ProductRecommendation.objects.create(primary=product_desc[num], recommendation=product_asc[num])

