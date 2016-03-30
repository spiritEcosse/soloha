from oscar.test import factories
from oscar.core.loading import get_model

ProductCategory = get_model('catalogue', 'productcategory')
Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class Test(object):
    @classmethod
    def create_categories(cls):
        """
        create bulk category
        Returns:
            None
        """
        category_1 = Category.objects.create(name='Category-1')
        category_12 = Category.objects.create(name='Category-12', parent=category_1)
        category_123 = Category.objects.create(name='Category-123', parent=category_12)
        category_1234 = Category.objects.create(name='Category-1234', parent=category_123)

        category_2 = Category.objects.create(name='Category-2')
        category_3 = Category.objects.create(name='Category-3')
        category_31 = Category.objects.create(name='Category-31', parent=category_3)
        category_32 = Category.objects.create(name='Category-32', parent=category_3)
        category_321 = Category.objects.create(name='Category-321', parent=category_32)
        category_33 = Category.objects.create(name='Category-33', parent=category_3)
        category_4 = Category.objects.create(name='Category-4')

    def create_product_bulk(self):
        """
        create bulk product with category and object image
        Returns:
            None
        """
        self.create_categories()

        for num in xrange(1, 10):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)
            category_123 = Category.objects.get(name='Category-123')
            category_3 = Category.objects.get(name='Category-3')
            category_32 = Category.objects.get(name='Category-32')
            product.categories.add(category_3, category_32, category_123)

        for num in xrange(10, 20):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)
            category_4 = Category.objects.get(name='Category-4')
            category_3 = Category.objects.get(name='Category-3')
            category_12 = Category.objects.get(name='Category-12')
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_3, category_12, category_321, category_4)

        for num in xrange(40, 50):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_321)

        for num in xrange(50, 60):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)

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

    @classmethod
    def create_order(cls):
        for num in xrange(1, 20):
            factories.create_order()
