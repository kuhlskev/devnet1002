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

module: cisco_asa_network_objectgroup
author: Patrick Ogenstad (@networklore) and Kevin Kuhls
version: 1.0
short_description: Creates deletes or edits network object-groups.
description:
    - Configures network object-groups
requirements:
options:
    category:
        description:
            - The type of object you are creating. Use slash notation for networks, i.e. 192.168.0.0/24. Use - for ranges, i.e. 192.168.0.1-192.168.0.10. 
        choices: [ 'ipv4_address', 'ipv6_address', 'ipv4_subnet', 'ipv6_subnet', 'ipv4_range', 'ipv6_range', 'ipv4_fqdn', 'ipv6_fqdn', 'object', 'object_group' ]
        required: false
    description:
        description:
            - Description of the object
        required: false
    entry_state:
        description:
            - State of the entire object-group
        choices: [ 'present', 'absent' ]
        required: false
    host:
        description:
            - Typically set to {{ inventory_hostname }}
        required: true
    members:
        description:
            - NOT YET IMPLEMENTED Variable containing all the objects within the network object-group
        required: false
    name:
        description:
            - Name of the network object
        required: true
    password:
        description:
            - Password for the device
        required: true
    state:
        description:
            - State of the entire object-group
        choices: [ 'present', 'absent' ]
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
    value:
        description:
            - The data to enter into the network object
        required: false

'''

EXAMPLES = '''

# Create a network object for a web server
- cisco_asa_network_object:
    host={{ inventory_hostname }}
    username=api_user
    password=APIpass123
    name=tsrv-web-1
    state=present
    category=IPv4Address
    description='Test web server'
    value='10.12.30.10'
    validate_certs=no

# Remove test webserver
- cisco_asa_network_object:
    host={{ inventory_hostname }}
    username=api_user
    password=APIpass123
    name=tsrv-web-2
    state=absent
    validate_certs=no
'''
import json

import sys
from ansible.module_utils.basic import *
from collections import defaultdict
import requests
from requests.auth import HTTPBasicAuth
#requests.packages.urllib3.disable_warnings()

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

class ASA(object):

    def __init__(self, device=None, username=None, password=None, verify_cert=False, timeout=30):
        
        self.device = device
        self.username = username
        self.password = password
        self.verify_cert = verify_cert
        self.timeout = timeout
        self.cred = HTTPBasicAuth(self.username, self.password)

    ######################################################################
    # General Functions
    ######################################################################
    def _delete(self, request):
        url = 'https://' + self.device + '/api/' + request
        data = requests.delete(url,headers=HEADERS,auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _get(self, request):
        url = 'https://' + self.device + '/api/' + request
        data = requests.get(url,headers=HEADERS,auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _patch(self, request, data):
        url = 'https://' + self.device + '/api/' + request
        data = requests.patch(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _post(self, request, data=False):
        url = 'https://' + self.device + '/api/' + request
        if data != False:
            data = requests.post(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        else:
            data = requests.post(url, headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)            
        return data

    def _put(self, request, data):
        url = 'https://' + self.device + '/api/' + request
        data = requests.put(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    ######################################################################
    # Functions related to network object-groups, or
    # "object-group network" in the ASA configuration
    ######################################################################

    def add_member_networkobjectgroup(self, net_object, member_data):
        request = 'objects/networkobjectgroups/' + net_object
        data = {}
        data['members.add'] = member_data
        return self._patch(request, data)

    def create_networkobjectgroup(self, data):
        request = 'objects/networkobjectgroups'
        return self._post(request, data)

    def delete_networkobjectgroup(self, net_object):
        request = 'objects/networkobjectgroups/' + net_object
        return self._delete(request)

    def get_networkobjectgroup(self, net_object):
        request = 'objects/networkobjectgroups/' + net_object
        return self._get(request)

    def get_networkobjectgroups(self):
        request = 'objects/networkobjectgroups'
        return self._get(request)

    def remove_member_networkobjectgroup(self, net_object, member_data):
        request = 'objects/networkobjectgroups/' + net_object
        data = {}
        data['members.remove'] = member_data
        return self._patch(request, data)

    def update_networkobjectgroup(self, net_object, data):
        request = 'objects/networkobjectgroups/' + net_object
        return self._patch(request, data)

object_kind = {
    'ipv4_address': 'IPv4Address',
    'ipv6_address': 'IPv6Address',
    'ipv4_subnet': 'IPv4Network',
    'ipv6_subnet': 'IPv6Network',
    'ipv4_range': 'IPv4Range',
    'ipv6_range': 'IPv6Range',
    'ipv4_fqdn': 'IPv4FQDN',
    'ipv6_fqdn': 'IPv6FQDN',
    'object': 'objectRef#NetworkObj',
    'object_group': 'objectRef#NetworkObjGroup'
}

object_kind_type = {
    'ipv4_address': 'value',
    'ipv6_address': 'value',
    'ipv4_subnet': 'value',
    'ipv6_subnet': 'value',
    'ipv4_range': 'value',
    'ipv6_range': 'value',
    'object': 'objectId',
    'object_group': 'objectId',
}

def add_object(dev, module, net_object, member_data):
    try:
        result = dev.add_member_networkobjectgroup(net_object,[member_data])
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code != 204:
        module.fail_json(msg='Unable to add object - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return True


def create_object(dev, module, desired_data):
    try:
        result = dev.create_networkobjectgroup(desired_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code == 201:
        return_status = True
    else:
        module.fail_json(msg='Unable to create object - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return return_status

def delete_object(dev, module, name):
    try:
        result = dev.delete_networkobjectgroup(name)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code == 204:
        return_status = True
    else:
        module.fail_json(msg='Unable to delete object - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return return_status

def find_member(current_data, desired_data, module):

    member_exists = False
    for member in current_data['members']:
        if member == desired_data:
            member_exists = True

    return member_exists

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            members=dict(required=False, type ="list", default=[]),  
            name=dict(required=True),
            entry_state=dict(required=False, choices=['absent', 'present'], default='present'),
            description=dict(required=False),
            state=dict(required=True, choices=['absent', 'present']),
            #category=dict(required=False, choices=[ 'ipv4_address', 'ipv6_address', 'ipv4_subnet', 'ipv6_subnet', 'ipv4_range', 'ipv6_range', 'ipv4_fqdn', 'ipv6_fqdn', 'object', 'object_group' ]),
            validate_certs=dict(required=False, type='bool', default=False),
            value=dict(required=False, default='Empty')
            ),
        #required_together = (
         #       ['entry_state','value'],
         #   ),
        #mutually_exclusive=(['category', 'members'],),
        supports_check_mode=False)

    m_args = module.params
    #if m_args['validate_certs'] == 'yes':
    #    validate_certs = true
    #else:
    #    validate_certs = false

    dev = ASA(
        device=m_args['host'],
        username=m_args['username'],

        password=m_args['password'],
        verify_cert=m_args['validate_certs']
    )
    members = []
    changed = False
    if m_args['members'] == []:
        members.append(m_args["value"])
    else:
        x = 0
        for item in m_args['members']:
            members.append(m_args['members'][x])
            x = x+1
    changed = False
    for value in members:
        #find category
        if '/32' in value:
            value = value.split('/')[0]  #API rejects /32 network objects, must convert to host
        if '/' in value:
            category = 'ipv4_subnet'
        elif '.' in value:
            category = 'ipv4_address'
        else:
            category = 'object_group'
        desired_data = {}
        desired_data['name'] = m_args['name']
        if m_args['description']:
            desired_data['description'] = m_args['description']
        #module.fail_json(msg='Testing - %s %s %s' % (value, category, m_args['state']))
        member_data = {}
        if m_args['entry_state']:
            member_data['kind'] = object_kind[category]
            kind_type = object_kind_type[category]
            member_data[kind_type] = value
            if kind_type == 'objectId':
                if category == 'object_group':
                    ref_link = 'https://%s/api/objects/networkobjectgroups/%s' % (m_args['host'], value)
                else:
                    ref_link = 'https://%s/api/objects/networkobjects/%s' % (m_args['host'], value)
                member_data['refLink'] = ref_link
    
            desired_data['members'] = [member_data]
        if m_args['members']:
            pass
    
        try:
            data = dev.get_networkobjectgroup(m_args['name'])
        except:
            err = sys.exc_info()[0]
            module.fail_json(msg='Unable to connect to device: %s' % err)
    
        if data.status_code == 200:
            if m_args['state'] == 'absent':
                changed_status = delete_object(dev, module, m_args['name'])
    
            elif m_args['state'] == 'present' and m_args['entry_state']:
    
                change_description = False
                if m_args['description']:
                    current_data = data.json()
                    try:
                        if m_args['description'] == current_data['description']:
    
                            change_description = False
                        else:
                            change_description = True
                    except:
                        change_description = True
    
                found = find_member(data.json(), member_data, module)
                #module.fail_json(msg="test %s %s" % (found, member_data))
                if found and m_args['entry_state'] == 'present':
                    changed_status = False
                elif found and m_args['entry_state'] == 'absent':
                    changed_status = remove_object(dev, module, m_args['name'], member_data)
    
                elif m_args['entry_state'] == 'present':
                    changed_status = add_object(dev, module, m_args['name'], member_data)
    
                elif m_args['entry_state'] == 'absent':
                    changed_status = False                
    
                if change_description:
                    changed_status = modify_description(dev, module, m_args['name'],m_args['description'])
    
            elif m_args['state'] == 'present' and m_args['members']:
                module.fail_json(msg='This feature is eagerly awaiting to be developed')
    
            else:
               #Remove after members are implemented
               module.fail_json(msg='Unknown error check arguments') 
    
        elif data.status_code == 401:
            module.fail_json(msg='Authentication error')
    
        elif data.status_code == 404:
            if m_args['state'] == 'absent':
                changed_status = False
            elif m_args['state'] == 'present':
                changed_status = create_object(dev, module, desired_data)
        else:
            module.fail_json(msg="Unsupported return code %s" % data.status_code)
        if changed == False:
            changed = changed_status
    return_msg = {}
    return_msg['changed'] = changed

    module.exit_json(**return_msg)

def modify_description(dev, module, net_object, description):
    data = {}
    data['description'] = description
    try:
        result = dev.update_networkobjectgroup(net_object, data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code != 204:
        module.fail_json(msg='Unable to change description - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return True
    
def remove_object(dev, module, net_object, member_data):
    try:
        result = dev.remove_member_networkobjectgroup(net_object,[member_data])
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code != 204:
        module.fail_json(msg='Unable to remove object - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return True

def update_object(dev, module, desired_data):
    try:
        result = dev.update_networkobject(desired_data['name'], desired_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code == 204:
        return_status = { 'changed': True }
    else:
        module.fail_json(msg='Unable to update object code: - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return return_status



main()

