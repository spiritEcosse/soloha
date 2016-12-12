from djng.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.utils.translation import ugettext_lazy as _
from django import forms

from dal import autocomplete

from apps.catalogue import models as catalogue_models
from apps.order.models import QuickOrder


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
            'phone_number': forms.TextInput(
                attrs={'title': _('You phone number'), 'ng-pattern': catalogue_models.REGEXP_PHONE}
            ),
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
        model = catalogue_models.ProductImage
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
        }


class FeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = catalogue_models.Feature
        widgets = {
            'parent': autocomplete.ModelSelect2(url='feature-autocomplete'),
        }


class ProductRecommendationForm(forms.ModelForm):
    class Meta:
        model = catalogue_models.ProductRecommendation
        fields = '__all__'
        widgets = {
            'recommendation': autocomplete.ModelSelect2(url='product-autocomplete'),
            'primary': autocomplete.ModelSelect2(url='product-autocomplete')
        }


class ProductFeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = catalogue_models.ProductFeature
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
            'feature': autocomplete.ModelSelect2(url='feature-autocomplete'),
            'product_with_images': autocomplete.ModelSelect2Multiple(url='product-autocomplete'),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = catalogue_models.Category
        widgets = {
            'parent': autocomplete.ModelSelect2(url='categories-autocomplete'),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = catalogue_models.Product
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
