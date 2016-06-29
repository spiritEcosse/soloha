from djangular.styling.bootstrap3.forms import Bootstrap3Form
from django import forms
from django.utils.translation import ugettext_lazy as _


class Subscribe(Bootstrap3Form):
    confirmation_key = forms.CharField(max_length=40, required=True, widget=forms.HiddenInput(),
                                       initial='hidden value')
    name = forms.CharField(max_length=30, label=_('Name'), required=True)
    city = forms.CharField(max_length=30, label=_('Name'), required=True)
    email = forms.EmailField(required=True, label=_('Email'),
                             error_messages={'required': _('Please enter your email.')},
                             widget=forms.widgets.EmailInput(
                                 attrs={'ng-pattern': r'/^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$/'}))
