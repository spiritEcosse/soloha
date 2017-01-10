from oscar.core.loading import get_model
from djangular.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form
from django.utils.translation import ugettext_lazy as _
from django import forms
from apps.catalogue.abstract_models import REGEXP_PHONE
from dal import autocomplete

from apps.catalogue.models import SortFeatureInCategory


QuickOrder = get_model('order', 'QuickOrder')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
Feature = get_model('catalogue', 'Feature')
Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')
ProductFeature = get_model('catalogue', 'ProductFeature')
StockRecord = get_model('partner', 'StockRecord')
Partner = get_model('partner', 'Partner')
Info = get_model('sites', 'Info')


class QuickOrderMeta(type(NgModelForm), type(Bootstrap3Form)):
    pass


class QuickOrderForm(NgModelForm, NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    __metaclass__ = QuickOrderMeta
    scope_prefix = 'quick_order_data'
    form_name = 'quick_order_form'

    class Meta:
        model = QuickOrder
        fields = ['phone_number', 'name', 'comment', 'email', 'product']
        widgets = {
            'comment': forms.Textarea(attrs={'title': _('You comment'), 'rows': 5}),
            'name': forms.TextInput(attrs={'title': _('You name')}),
            'phone_number': forms.TextInput(attrs={'title': _('You phone number'), 'ng-pattern': REGEXP_PHONE}),
            'email': forms.TextInput(attrs={'title': _('You email')}),
            'product': forms.HiddenInput()
        }
        labels = {
            'name': _('You name'),
            'phone_number': _('You phone number'),
            'comment': _('You comment'),
            'email': _('You email')
        }
        error_messages = {
            'name': {
                'require': _('This field required.'),
            },
            'phone_number': {
                'require': _('This field required.')
            }
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = ProductImage
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
        }


class FeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Feature
        widgets = {
            'parent': autocomplete.ModelSelect2(url='feature-autocomplete'),
        }


class ProductRecommendationForm(forms.ModelForm):
    class Meta:
        model = ProductRecommendation
        fields = '__all__'
        widgets = {
            'recommendation': autocomplete.ModelSelect2(url='product-autocomplete'),
            'primary': autocomplete.ModelSelect2(url='product-autocomplete')
        }


class ProductFeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = ProductFeature
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
            'feature': autocomplete.ModelSelect2(url='feature-autocomplete'),
            'product_with_images': autocomplete.ModelSelect2Multiple(url='product-autocomplete'),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Category
        widgets = {
            'parent': autocomplete.ModelSelect2(url='categories-autocomplete'),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'parent': autocomplete.ModelSelect2(url='product-autocomplete'),
            'partner': autocomplete.ModelSelect2(url='partner-autocomplete'),
            'filters': autocomplete.ModelSelect2Multiple(url='feature-autocomplete'),
            'categories': autocomplete.ModelSelect2Multiple(url='categories-autocomplete'),
            'characteristics': autocomplete.ModelSelect2Multiple(url='feature-autocomplete'),
        }

    def clean(self):
        super(ProductForm, self).clean()
        characteristics = list(self.cleaned_data['characteristics'])
        characteristics.extend(self.cleaned_data['filters'])
        self.cleaned_data['characteristics'] = characteristics
        return self.cleaned_data


class SortFeatureInCategoryForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = SortFeatureInCategory
        widgets = {
            'feature': autocomplete.ModelSelect2(url='feature-autocomplete'),
            'category': autocomplete.ModelSelect2(url='categories-autocomplete'),
        }
