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

'''
Module containing the backends for pyssf.
'''
import uuid

from api import occi_ext
from occi import backend
from adapters import ops2, ops3


class AppBackend(backend.KindBackend, backend.ActionBackend):
    '''
    Handle PaaS based Applications.
    '''

    def __init__(self, paas_adapter):
        self.glue = paas_adapter

    def create(self, entity, extras):
        if 'occi.app.name' not in entity.attributes:
            raise AttributeError('occi.app.name is a required attribute')

        app_temp = None
        res_temp = None
        for mixin in entity.mixins:
            if isinstance(mixin, occi_ext.AppTemplate):
                app_temp = mixin
            if isinstance(mixin, occi_ext.ResTemplate):
                res_temp = mixin

        scaling = {'scale': 'False'}
        if 'occi.app.scale' in entity.attributes:
            scaling['scale'] = entity.attributes['occi.app.scale']
            if 'occi.app.scales_from' in entity.attributes:
                scaling['scales_from'] = entity.attributes['occi.app.scales_from']
            if 'occi.app.scales_to' in entity.attributes:
                scaling['scales_to'] = entity.attributes['occi.app.scales_to']

        name = entity.attributes['occi.app.name']
        # OpS2 Specific: no problem if there is no mixin in OpS3 when directly deploying docker containers
        if self.glue.PLATFORM is 'OpenShift2':
            if not app_temp or not res_temp:
                raise AttributeError('Please provide a valid App and '
                                     'Resource Template.')

            tmp = self.glue.create_app(name, app_temp.term, res_temp.term,
                                   extras['auth_header'], **scaling)
        elif self.glue.PLATFORM is 'OpenShift3':
            # no need for extra info besides docker image
            docker_image = env_vars = None
            if 'occi.app.docker_image' in entity.attributes:
                docker_image = entity.attributes['occi.app.docker_image']
            if 'occi.app.env' in entity.attributes:
                env_vars = entity.attributes['occi.app.env']
            if not docker_image:
                raise AttributeError('Please provide a valid docker image name.')

            tmp = self.glue.create_app(name, docker_image, extras['auth_header'], env=env_vars)
        else:
            # raise AttributeError('Invalid GLUE chosen in CC API.')
            # TODO: For testing purposes, better to not raise that and instead have the default OpS behaviour
            if not app_temp or not res_temp:
                raise AttributeError('Please provide a valid App and '
                                     'Resource Template.')

            tmp = self.glue.create_app(name, app_temp.term, res_temp.term,
                                   extras['auth_header'], **scaling)
        # OpS2 compatibility
        uid = tmp['data']['id']
        scale = tmp['data']['scalable']
        entity.attributes['occi.app.scale'] = scale
        entity.attributes['occi.core.id'] = uid
        entity.identifier = '/app/' + uid

    def retrieve(self, entity, extras):
        uid = entity.attributes['occi.core.id']
        tmp, tmp2 = self.glue.retrieve_app(uid, extras['auth_header'])

        # update attributes
        # next two are generic
        entity.attributes['occi.app.url'] = tmp['data']['app_url']
        entity.attributes['occi.app.name'] = tmp['data']['name']
        if 'git_url' in tmp['data']:  # Indicates OpS2 at the moment
            entity.attributes['occi.app.repo'] = tmp['data']['git_url']
            state = tmp2['data'][0]['gears'][0]['state']
            if state in ['started']:
                entity.attributes['occi.app.state'] = 'active'
                entity.actions = [occi_ext.APP_STOP]
            else:
                entity.attributes['occi.app.state'] = 'inactive'
                entity.actions = [occi_ext.APP_START]
            # update scaling status - only exists in OpS2 as OpS3 only indicates current replicas for each pod
            entity.attributes['occi.app.scale'] = tmp['data']['scalable']
            entity.attributes['occi.app.scales_from'] = tmp2['data'][0]['scales_from']
            entity.attributes['occi.app.scales_to'] = tmp2['data'][0]['scales_to']
        else:  # Indicates OpS3 - Better would be a version indicator somewhere
            if tmp['data']['state']:
                entity.attributes['occi.app.state'] = 'active'
            else:
                entity.attributes['occi.app.state'] = 'inactive'
                # no actions configured at the moment on the service

    def delete(self, entity, extras):
        uid = entity.attributes['occi.core.id']
        self.glue.delete_app(uid, extras['auth_header'])

    def action(self, entity, action, attributes, extras):
        uid = entity.attributes['occi.core.id']
        if action not in entity.actions:
            raise AttributeError('This action is currently not applicable.')
        elif action == occi_ext.APP_START:
            self.glue.start_app(uid, extras['auth_header'])
        elif action == occi_ext.APP_STOP:
            self.glue.stop_app(uid, extras['auth_header'])
        entity.actions = []


class ServiceLink(backend.KindBackend):
    '''
    Backend for the service links.
    '''

    def __init__(self, paas_adapter):
        self.glue = paas_adapter

    def create(self, entity, extras):
        iden = entity.source.identifier.split('/')[-1:][0]
        name = entity.target.identifier.split('/')[-1:][0]
        self.glue.add_service(iden, name, extras['auth_header'])

    def delete(self, entity, extras):
        iden = entity.source.identifier.split('/')[-1:][0]
        name = entity.target.identifier.split('/')[-1:][0]
        self.glue.delete_service(iden, name, extras['auth_header'])


class SshKeyBackend(backend.KindBackend):
    '''
    Backend handling ssh keys.
    '''

    def __init__(self, paas_adapter):
        self.glue = paas_adapter

    def create(self, entity, extras):
        if 'occi.key.name' not in entity.attributes:
            name = 'key_' + str(uuid.uuid4())
        else:
            name = entity.attributes['occi.key.name']
        if 'occi.key.content' not in entity.attributes:
            raise AttributeError('Key value is required.')
        content = entity.attributes['occi.key.content']
        entity.attributes['occi.core.id'] = name
        self.glue.add_key(name, content, extras['auth_header'])

    def delete(self, entity, extras):
        uid = entity.attributes['occi.core.id']
        self.glue.delete_key(uid, extras['auth_header'])
