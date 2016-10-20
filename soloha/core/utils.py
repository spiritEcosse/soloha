from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _, pgettext_lazy


class CommonFeatureProduct(object):
    @property
    def product_slug(self):
        return self.product.slug

    def product_enable(self):
        return self.product.enable
    product_enable.short_description = _('Enable product')

    def product_categories_to_str(self):
        return self.product.categories_to_str()
    product_categories_to_str.short_description = _("Categories")

    def product_partner(self):
        return self.product.partner
    product_partner.short_description = _("Product partner")

    def thumb(self, image=None):
        if not image:
            image = self.product.primary_image()

        return loader.get_template(
            'admin/catalogue/product/thumb.html'
        ).render(
            Context(
                {
                    'image': image
                }
            )
        )
    thumb.allow_tags = True
    thumb.short_description = _('Image of product')

    def product_date_updated(self):
        return self.product.date_updated
    product_date_updated.short_description = _("Product date updated")
