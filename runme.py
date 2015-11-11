#!/usr/bin/env python

#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from api import wsgi
import logging
import signal

from tornado import httpserver
from tornado import ioloop
from tornado import wsgi as t_wsgi


logging.basicConfig(level='DEBUG')
LOG = logging.getLogger(__name__)


def shutdown():
    print 'Goodbye cruel world...'
    ioloop.IOLoop.instance().stop()


def sig_handler(sig, frame):
    ioloop.IOLoop.instance().add_callback(shutdown)

if __name__ == '__main__':
    app = wsgi.get_app()
    container = t_wsgi.WSGIContainer(app)
    http_server = httpserver.HTTPServer(container)
    http_server.listen(8888)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    i = ioloop.IOLoop.instance().start()
