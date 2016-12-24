from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from soloha.core.forms.fields import ExtendedURLField
from soloha.core.loading import get_classes

RawHTML, PagePromotion = get_classes('promotions.models', ['RawHTML', 'PagePromotion'])


class RawHTMLForm(forms.ModelForm):
    class Meta:
        model = RawHTML
        fields = ['name', 'body']


class PagePromotionForm(forms.ModelForm):
    page_url = ExtendedURLField(label=_("URL"), verify_exists=True)
    position = forms.CharField(
        widget=forms.Select(choices=settings.PROMOTION_POSITIONS),
        label=_("Position"),
        help_text=_("Where in the page this content block will appear"))

    class Meta:
        model = PagePromotion
        fields = ['position', 'page_url']

    def clean_page_url(self):
        page_url = self.cleaned_data.get('page_url')
        if not page_url:
            return page_url

        if page_url.startswith('http'):
            raise forms.ValidationError(
                _("Content blocks can only be linked to internal URLs"))

        if page_url.startswith('/') and not page_url.endswith('/'):
            page_url += '/'

        return page_url
