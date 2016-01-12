#!/usr/bin/env python

# Run this with
# PYTHONPATH=. DJANGO_SETTINGS_MODULE=cinema.settings tornado_main.py

import os
from soloha.settings import PROJECT_NAME
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % PROJECT_NAME)
from soloha.settings_local import AUTORELOAD

from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

if django.VERSION[1] > 5:
    django.setup()
import logging

define('port', type=int, default=8213)


def main():
    parse_command_line()
    wsgi_app = tornado.wsgi.WSGIContainer(
        django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application(
        [('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)), ], debug=True, autoreload=AUTORELOAD)
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    tornado.options.parse_command_line()
    logging.info('Starting up')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
