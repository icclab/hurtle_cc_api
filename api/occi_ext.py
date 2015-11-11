#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#   Copyright 2015 Zuercher Hochschule fuer Angewandte Wissenschaften
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

"""
OCCI model extensions supporting PaaS.
"""

import ConfigParser
import occi.core_model
import occi.extensions.infrastructure


CONFIG = ConfigParser.ConfigParser()
CONFIG.read('etc/defaults.cfg')
GLUE_NAME = CONFIG.get('General', 'platform')


# Security
KEY_ATTR = {'occi.key.name': '',
            'occi.key.content': 'required'}

KEY_KIND = occi.core_model.Kind('http://schemas.ogf.org/occi/security/'
                                'credentials#',
                                'public_key', title='A ssh key.',
                                attributes=KEY_ATTR,
                                related=[occi.core_model.Resource.kind])

# Definitions
APP_ATTR = None
if GLUE_NAME == 'OpenShift3':
    APP_ATTR = {'occi.app.name': 'required',
                'occi.app.state': 'immutable',
                'occi.app.image': 'required',
                'occi.app.env': ''}

elif GLUE_NAME == 'OpenShift2':
    APP_ATTR = {'occi.app.name': 'required',
                'occi.app.repo': 'immutable',
                'occi.app.url': 'immutable',
                'occi.app.state': 'immutable',
                'occi.app.scale': 'mutable',
                'occi.app.scales_from': 'mutable',
                'occi.app.scales_to': 'mutable'}

APP_START = occi.core_model.Action('http://schemas.ogf'
                                   '.org/occi/platform/app/action#',
                                   'start')
APP_STOP = occi.core_model.Action('http://schemas.ogf'
                                  '.org/occi/platform/app/action#',
                                  'stop')

APP = occi.core_model.Kind('http://schemas.ogf.org/occi/platform#', 'app',
                           title='A PaaS application.', attributes=APP_ATTR,
                           related=[occi.core_model.Resource.kind],
                           actions=[APP_START, APP_STOP])

COMPONENT = occi.core_model.Kind('http://schemas.ogf.org/occi/platform#',
                                 'component',
                                 title='An Service component.',
                                 related=[occi.core_model.Resource.kind])

COMP_LINK = occi.core_model.Kind('http://schemas.ogf.org/occi/platform#',
                                 'componentlink',
                                 related=[occi.core_model.Link.kind])

# Templates

APP_TEMPLATE = occi.core_model.Mixin('http://schemas.ogf.org/occi/platform#',
                                     'app_tpl')

# e.g. GEAR size in OpenShift
RES_TEMPLATE = occi.core_model.Mixin('http://schemas.ogf.org/occi/platform#',
                                     'res_tpl')

# Impl


class AppTemplate(occi.core_model.Mixin):
    """
    Application type template.
    """

    pass


class ResTemplate(occi.core_model.Mixin):
    """
    Resource template.
    """

    pass
