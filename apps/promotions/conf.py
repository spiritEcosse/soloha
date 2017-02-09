from apps.promotions.models import SingleProduct, RawHTML, Image, AutomaticProductList, \
    HandPickedProductList, MultiImage


def get_promotion_classes():
    return (RawHTML, Image, SingleProduct, AutomaticProductList, HandPickedProductList, MultiImage)


PROMOTION_CLASSES = get_promotion_classes()
