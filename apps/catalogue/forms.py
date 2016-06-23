from oscar.core.loading import get_model
from djangular.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form
from django.utils.translation import ugettext_lazy as _
from django import forms
from apps.catalogue.abstract_models import REGEXP_PHONE, REGEXP_EMAIL

QuickOrder = get_model('catalogue', 'QuickOrder')


class QuickOrderMeta(type(NgModelForm), type(Bootstrap3Form)):
    pass


class QuickOrderForm(NgModelForm, NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    __metaclass__ = QuickOrderMeta
    scope_prefix = 'quick_order_data'
    form_name = 'quick_order_form'

    class Meta:
        model = QuickOrder
        fields = ['phone_number', 'name', 'comment', 'email']
        widgets = {
            'comment': forms.Textarea(attrs={'title': _('You comment'), 'rows': 5}),
            'name': forms.TextInput(attrs={'title': _('You name')}),
            'phone_number': forms.TextInput(attrs={'title': _('You phone number'), 'ng-pattern': REGEXP_PHONE}),
            'email': forms.TextInput(attrs={'title': _('You email'), 'ng-pattern': REGEXP_EMAIL}),
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
