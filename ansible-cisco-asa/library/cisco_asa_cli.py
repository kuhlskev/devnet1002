#!/usr/bin/python

# Copyright 2015 Kevin Kuhls <kekuhls@cisco.com>
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
author: Kevin Kuhls
version: 1.0
short_description: Runs command on ASA via API.
description:
    - Issues the cli command on the unit
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
    cli:
        description:
            - Command to run on the device
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
    cli="mtu outside 1400"
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

    def __init__(self, device=None, username=None, password=None, verify_cert=False, timeout=5):
        
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

    def cli(self, cli):
        """Runs cli command on ASA
        """
        request = "cli"
        return self._post(request, cli)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            cli=dict(required=True),
            validate_certs=dict(required=False, type="bool", default=False),
        ),
        supports_check_mode=False)

    m_args = module.params
    cli=m_args['cli']
    dev = ASA(
        device=m_args['host'],
        username=m_args['username'],
        password=m_args['password'],
        verify_cert=m_args["validate_certs"]
    )
    desired_data = {}
    desired_data ['commands'] = [cli]
    #module.fail_json(msg="Module unable to create object - {}: \n".format(desired_data))
    try:
        data = dev.cli(desired_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if data.status_code == 200:
        return_status = True
    else:
        module.fail_json(msg='Unable to change configuration: - %s' % data.status_code)

    return_msg = { 'changed': return_status } 
    module.exit_json(**return_msg)
    
main()

