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
A PaaS dummy adapter.
'''

import json


class DummyPaas():
    '''
    Mimics OpS.
    '''

    status = 'started'

    def create_app(self, name, template, size, auth_head):
        return json.load(file('tests/json_payloads/create_app.json'))

    def retrieve_app(self, uid, auth_head):
        tmp1 = json.load(file('tests/json_payloads/retrieve_app.json'))
        tmp2 = json.load(file('tests/json_payloads/list_gears.json'))
        tmp2['data'][0]['gears'][0]['state'] = self.status
        return tmp1, tmp2

    def delete_app(self, uid, auth_head):
        return json.load(file('tests/json_payloads/delete_app.json'))

    def list_apps(self, auth_head):
        return json.load(file('tests/json_payloads/list_apps.json'))

    def list_features(self, auth_head):
        return json.load(file('tests/json_payloads/list_cartridges.json'))

    def list_gears(self, auth_head):
        return json.load(file('tests/json_payloads/user_capabilities.json'))

    def start_app(self, uid, auth_head):
        self.status = 'started'
        return json.load(file('tests/json_payloads/app_event.json'))

    def stop_app(self, uid, auth_head):
        self.status = 'stopped'
        return json.load(file('tests/json_payloads/app_event.json'))

    def add_service(self, uid, name, auth_head):
        pass

    def delete_service(self, uid, name, auth_head):
        pass

    def add_key(self, uid, content, auth_head):
        pass

    def delete_key(self, uid, auth_head):
        pass

    def list_keys(self, auth_head):
        return json.load(file('tests/json_payloads/list_ssh_keys.json'))
