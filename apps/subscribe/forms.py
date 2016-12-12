from djng.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from djng.styling.bootstrap3.forms import Bootstrap3Form

from django.utils.translation import ugettext_lazy as _
from django import forms
from apps.subscribe.models import Subscribe


class SubscribeMeta(type(NgModelForm), type(Bootstrap3Form)):
    pass


class SubscribeForm(NgModelForm, NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    __metaclass__ = SubscribeMeta
    scope_prefix = 'subscribe_data'
    form_name = 'subscribe_form'

    class Meta:
        model = Subscribe
        fields = ['email', 'name', 'city']
        labels = {
            'email': _('Your email'),
            'name': _('Your name'),
            'city': _('Your city')
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
