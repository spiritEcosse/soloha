from oscar.core.loading import get_model
from djangular.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form
from django.utils.translation import ugettext_lazy as _
from django import forms
# from apps.catalogue.abstract_models import REGEXP_PHONE

Subscribe = get_model('promotions', 'Subscribe')


class SubscribeMeta(type(NgModelForm), type(Bootstrap3Form)):
    pass


class SubscribeForm(NgModelForm, NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    __metaclass__ = SubscribeMeta
    scope_prefix = 'subscribe_data'
    form_name = 'subscribe_form'

    class Meta:
        model = Subscribe
        fields = ['email', 'name', 'city']
        widgets = {
            'city': forms.Textarea(attrs={'title': _('You comment'), 'rows': 5}),
            'name': forms.TextInput(attrs={'title': _('You name')}),
            'email': forms.TextInput(attrs={'title': _('You email')}),
        }
        labels = {
            'email': _('You email'),
            'name': _('You name'),
            'city': _('You city')
        }
        error_messages = {
            'email': {
                'require': _('This field required.'),
            },
            'name': {
                'require': _('This field required.'),
            },
            'city': {
                'require': _('This field required.')
            }
        }
