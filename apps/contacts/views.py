from django.shortcuts import render

from django.core.mail import send_mail
from django.views.generic import FormView
from forms import Feedback
from django.utils.translation import ugettext_lazy as _
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from django.http import HttpResponse
import json
from django.views.generic.base import ContextMixin
from django.utils import translation
from django.core.urlresolvers import reverse_lazy


class FeedbackForm(NgFormValidationMixin, Feedback):
    scope_prefix = 'feedback'
    form_name = 'form_comment'


class ContactsView(FormView, ContextMixin):
    template_name = 'contacts/contacts.html'
    form_class = FeedbackForm
    success_url = '/contacts/'

    def post(self, request, **kwargs):
        if request.is_ajax():
            raise Exception('gh')
            return self.ajax(request)
        return super(ContactsView, self).post(request, **kwargs)

    def ajax(self, request):
        raise Exception('TEST')
        form = self.form_class(data=json.loads(request.body))
        response_data = {'errors': form.errors}

        if not form.errors:
            send_mail(_('You received a letter from the site %s') % request.META['HTTP_HOST'],
                      'Email: %s .\nComment: %s' % (form.cleaned_data['email'], form.cleaned_data['comment']),
                      form.cleaned_data['email'], # [EMAIL_COMPANY],
                      fail_silently=False)
            response_data['msg'] = unicode(_('Your message sent!'))
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(ContactsView, self).get_context_data(**kwargs)
        # cur_language = translation.get_language()
        # context['class'] = ''
        #
        # if cur_language == 'ru':
        #     context['class'] = 'class=lang_ru'
        return context
