from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.template import RequestContext
from django.template import loader
from collections import namedtuple


HttpResponse = namedtuple('HttpResponse', ['title', 'template'])


class HttpResponseMiddleware(object):
    http_responses = (
        HttpResponse(title=HttpResponseNotAllowed, template='405.html'),
        HttpResponse(title=HttpResponseForbidden, template='403.html'),
        HttpResponse(title=HttpResponseNotFound, template='404.html'),
        HttpResponse(title=HttpResponseServerError, template='500.html'),
    )

    def process_response(self, request, response):
        http_response = filter(lambda http_response: isinstance(response, http_response.title), self.http_responses)

        if http_response:
            template = http_response[0].template
            context = RequestContext(request)
            response.content = loader.render_to_string(template, context_instance=context)

        return response
