from django.shortcuts import render

from django.core.mail import send_mail
from django.views.generic import FormView
from forms import Feedback
from django.utils.translation import ugettext_lazy as _
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from django.http import HttpResponse
import json
from django.views.generic.base import ContextMixin
from django.contrib.sites.shortcuts import get_current_site
# from apps.catalogue.models import SiteInfo


class FeedbackForm(NgModelFormMixin, NgFormValidationMixin, Feedback):
    scope_prefix = 'feedback'
    form_name = 'form_comment'


class ContactsView(FormView, ContextMixin):
    template_name = 'contacts/contacts.html'
    form_class = FeedbackForm

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(ContactsView, self).post(request, **kwargs)

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))
        response_data = {'errors': form.errors}

        if not form.errors:
            # email_to = SiteInfo.objects.get(domain=get_current_site(request).domain).email
            email_to = 'aw@gmail.com'
            form_email = form.cleaned_data['email']
            self.send_email(request, form, form_email, email_to)
            email_to, form_email = form_email, email_to
            self.send_email(request, form, form_email, email_to)

            response_data['msg'] = str(_('Sent!'))
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_email(self, request, form, form_email, email_to):
        send_mail(_('You received a letter from the site %s') % request.META['HTTP_HOST'],
                      'Email: %s .\nComment: %s' % (form_email, form.cleaned_data['comment']),
                      form.cleaned_data['email'], [email_to],
                      fail_silently=False)
