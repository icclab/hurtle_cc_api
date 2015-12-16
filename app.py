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

from wsgiref.simple_server import make_server
import thread
from api import admin
from api import wsgi

import logging

logging.basicConfig(level='DEBUG')
LOG = logging.getLogger(__name__)

if __name__ == '__main__':
    thread.start_new_thread(admin.server, ('0.0.0.0', 8081))
    app = wsgi.get_app()
    httpd = make_server('0.0.0.0', 8080, app)
    LOG.info('Listening on http://0.0.0.0:8080')
    httpd.serve_forever()
