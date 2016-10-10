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
from braces import views
from braces import views


class FeedbackForm(NgModelFormMixin, NgFormValidationMixin, Feedback):
    scope_prefix = 'feedback'
    form_name = 'form_comment'


class ContactsView(FormView, ContextMixin, views.JSONResponseMixin):
    template_name = 'contacts/contacts.html'
    form_class = FeedbackForm
    form_valid_message = unicode(_('You question has been sent!'))

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(ContactsView, self).post(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactsView, self).get_context_data(**kwargs)
        initial_data = {}

        if self.request.user.is_authenticated():
            initial_data['name'] = self.request.user.username
            initial_data['email'] = self.request.user.email

        context['form'] = self.form_class(initial=initial_data)
        return context

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))

        if form.is_valid():
            email_to = get_current_site(request).info.email
            form_email = form.cleaned_data['email']
            self.send_email(form, form_email, email_to)

            response_data = {'msg': self.form_valid_message}
        else:
            response_data = {'errors': form.errors}

        return self.render_json_response(response_data)

    def send_email(self, form, form_email, email_to):
        send_mail(
            unicode(_('You received a letter from the site {}'.format(get_current_site(self.request).domain))),
            unicode(_(u'User name: {}.\nEmail: {}.\nPhone: {}.\nComment: {}.'.format(
                form.cleaned_data.get('name', str(_('Not specified.'))),
                form_email,
                form.cleaned_data.get('phone', str(_('Not specified.'))),
                form.cleaned_data['comment']
            ))),
            form_email,
            [email_to],
            fail_silently=False
        )
