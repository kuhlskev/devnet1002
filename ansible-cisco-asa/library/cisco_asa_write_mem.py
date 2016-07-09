#!/usr/bin/python

# Copyright 2015 Patrick Ogenstad <patrick@ogenstad.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = '''
---

module: cisco_asa_write_mem
author: Patrick Ogenstad (@networklore)
version: 1.0
short_description: Saves the configuration.
description:
    - Issues the write mem command on the unit
requirements:
    - rasa
options:
    host:
        description:
            - Typically set to {{ inventory_hostname }}
        required: true
    password:
        description:
            - Password for the device
        required: true
    username:
        description:
            - Username for device
        required: true
    validate_certs:
        description:
            - If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
        choices: [ 'no', 'yes']
        default: 'yes'
        required: false
'''

EXAMPLES = '''

# Save the running configuration
- cisco_asa_write_mem:
    host={{ inventory_hostname }}
    username=api_user
    password=APIpass123
    validate_certs=no

'''

import sys
from ansible.module_utils.basic import *
from collections import defaultdict
import requests
from requests import Request
from requests.auth import HTTPBasicAuth
#requests.packages.urllib3.disable_warnings()

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
#    "User-Agent": "RASA"
}

class ASA(object):

    def __init__(self, device=None, username=None, password=None, verify_cert=False, timeout=30):
        
        self.device = device
        self.username = username
        self.password = password
        self.verify_cert = verify_cert
        self.timeout = timeout
        self.cred = HTTPBasicAuth(self.username, self.password)

    def _post(self, request, data=False):
        url = "https://" + self.device + "/api/" + request
        if data != False:
            data = requests.post(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        else:
            data = requests.post(url, headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)            
        return data

    def write_mem(self):
        """Saves the running configuration to memory
        """
        request = "commands/writemem"
        return self._post(request)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            validate_certs=dict(required=False, type="bool", default=False),
        ),
        supports_check_mode=False)

    m_args = module.params

    dev = ASA(
        device=m_args['host'],
        username=m_args['username'],
        password=m_args['password'],
        verify_cert=m_args["validate_certs"]
    )

    try:
        data = dev.write_mem()
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if data.status_code == 200:
        return_status = True
    else:
        module.fail_json(msg='Unable to save configuration: - %s' % data.status_code)

    return_msg = { 'changed': return_status } 
    module.exit_json(**return_msg)
    
main()

