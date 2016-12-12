import json

from braces import views
from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from apps.subscribe.forms import SubscribeForm
from apps.ex_sites.models import Info
from apps.subscribe.models import Subscribe

from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader, Context
from django.core.urlresolvers import reverse_lazy


ANSWER = str(_('Subscribed successfully!'))


class SubscribeView(views.JSONResponseMixin, views.AjaxResponseMixin, FormView):
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
    model = Subscribe
    template_send_email = 'subscribe/subscribe.html'

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(SubscribeView, self).post(request, **kwargs)

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))
        response_data = {}

        if form.is_valid():
            form.save()
            self.form = form.save(commit=False)
            self.send_message()
        else:
            response_data = {'errors': form.errors}

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_message(self):
        current_site = Info.objects.get(domain=get_current_site(self.request).domain)
        subject = str(_('Order online %s')) % current_site.domain

        from_email = current_site.email
        context = {'object': self.form, 'current_site': current_site}

        if self.form.email:
            context_user = context
            context_user = context_user.update({'answer': ANSWER})
            message = loader.get_template(self.template_send_email).render(Context(context_user))
            from_email = self.form.email
            msg = EmailMultiAlternatives(subject, '', current_site.email, [self.form.email])
            msg.attach_alternative(message, "text/html")
            msg.send()

        message = loader.get_template(self.template_send_email).render(Context(context))
        msg = EmailMultiAlternatives(subject, '', from_email, [current_site.email])
        msg.attach_alternative(message, "text/html")
        msg.send()

