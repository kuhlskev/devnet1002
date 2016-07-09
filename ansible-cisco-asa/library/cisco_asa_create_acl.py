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
short_description: Creates ACL entry on ASA
description:
    - Issues the command to create an access-list entry on the unit
requirements:
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
    acl_name:
        description:
            - The name of the Access-List to create or append an entry to
        required: True
    permit: 
        description:
            - The ACE is to perimt or deny traffic
        choices: [ 'True', 'False']
        default: True
        required: False
    protocol:
        description:
            - The protocol of the ACE
        choices: [ 'ip', 'tcp', 'udp']
    source_service:
        description:
            - The Source service is one of three options, 
                - if empty "any" is chosen
                - if an integer, then the port is the integer value passed
                - if a string, then an object-group with the name of the string
              Note: names for known protocols is not permitted, i.e http,ssh, etc
    source_address:
        description:
            - The Source address is one of three options
                - if empty "any" is chosen
                - it it contains the '.' character it is assumed to be an IP address
                - if it is a string not containing a '.' character a network object group named by the string is used
    destination_service:
        description:
            - The Source service is one of three options, 
                - if empty "any" is chosen
                - if an integer, then the port is the integer value passed
                - if a string, then an object-group with the name of the string
              Note: names for known protocols is not permitted, i.e http,ssh, etc
    destination_address:
        description:
            - The Source address is one of three options
                - if empty "any" is chosen
                - it it contains the '.' character it is assumed to be an IP address
                - if it is a string not containing a '.' character a network object group named by the string is used
    entry:
        description
            - The details of the access-list entry as a dictionary.
            To be used in lieu of source_address, source_service, destination_service, destination_address variables individually
    position:
         description:
            - This represents the position of the ACE within the ACL.  This is also called the line or entry.
            If empty the integer 1 is assumed.  The assumption is ACL's to be added are permissive and therefore 
            the logic is adding ACL's to the top
            Note: Make sure to set line for DENY ACL Entries.  By defaul they would be added to the top and likely 
            disallow intended access of Permit ACL entried below.    
'''

EXAMPLES = '''
- kev_asa_create_acl:
    host: "{{ inventory_hostname }}"
    username: 'api_user'
    password: 'keviniscool'
    validate_certs: False
    acl_name: 'kevacl'
    permit: true
    protocol: tcp
    source_service: 'web-ports'
    source_address: 'my-object-group'
    destination_service: 432
    destination_address: '3.4.6.12'
    position: 1
'''

#import base64
import json, ast, string, requests
#import sys
#import urllib2
#import ssl
from ansible.module_utils.basic import *
from requests.auth import HTTPBasicAuth

HEADERS = {
'Content-Type': 'application/json',
'Accept': 'application/json',
}
tcp_services = {
    "7": "echo",
    "9": "discard",
    "13": "daytime",
    "19": "chargen",
    "20": "ftp-data",
    "21": "ftp",
    "22": "ssh",
    "23": "telnet",
    "25": "smtp",
    "43": "whois",
    "49": "tacacs",
    "53": "domain",
    "70": "gopher",
    "79": "finger",
    "80": "http",
    "101": "hostname",
    "109": "pop2",
    "110": "pop3",
    "111": "sunrpc",
    "113": "ident",
    "119": "nntp",
    "139": "netbios-ssn",
    "143": "imap4",
    "179": "bgp",
    "194": "irc",
    "389": "ldap",
    "443": "https",
    "496": "pim-auto-rp",
    "512": "exec",
    "513": "login",
    "514": "rsh",
    "515": "lpd",
    "517": "talk",
    "540": "uucp",
    "543": "klogin",
    "544": "kshell",
    "554": "rtsp",
    "636": "ldaps",
    "750": "kerberos",
    "1352": "lotusnotes",
    "1494": "citrix-ica",
    "1521": "sqlnet",
    "1720": "h323",
    "1723": "pptp",
    "2049": "nfs",
    "2748": "ctiqbe",
    "3020": "cifs",
    "5060": "sip",
    "5190": "aol",
    "5631": "pcanywhere-data"    
}

udp_services = {
    "7": "echo",
    "9": "discard",
    "37": "time",
    "42": "nameserver",
    "49": "tacacs",
    "53": "domain",
    "67": "bootps",
    "68": "bootpc",
    "69": "tftp",
    "80": "www",
    "111": "sunrpc",
    "123": "ntp",
    "137": "netbios-ns",
    "138": "netbios-dgm",
    "161": "snmp",
    "162": "snmptrap",
    "177": "xdmcp",
    "195": "dnsix",
    "434": "mobile-ip",
    "496": "pim-auto-rp",
    "500": "isakmp",
    "512": "biff",
    "513": "who",
    "514": "syslog",
    "517": "talk",
    "520": "rip",
    "750": "kerberos",
    "1645": "radius",
    "1646": "radius-acct",
    "2049": "nfs",
    "3020": "cifs",
    "4789": "vxlan",
    "5060": "sip",
    "5510": "secureid-udp",
    "5632": "pcanywhere-status"    
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

    def create_acl(self, data, acl_name):
        request = 'objects/extendedacls/' + acl_name + '/aces'
        return self._post(request, data)

    def delete_acl(self, objectId, acl_name):
        request = 'objects/extendedacls/' + acl_name + '/aces/' + objectId
        return self._delete(request)

    def get_acls(self, acl_name):
        request = 'objects/extendedacls/' + acl_name + '/aces'
        return self._get(request)


def add_acl(dev, module, member_data, acl_name):
    try:
        result = dev.create_acl(member_data, acl_name)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code != 201:
        module.fail_json(msg='Unable to add access-list entry - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return True


def delete_acl(dev, module, current_data, desired_data, acl_name):
    for member in current_data['items']:
        try: del member['destinationAddress']['refLink']
        except: pass
        try: del member['sourceAddress']['refLink']
        except: pass
        try: del member['destinationService']['refLink']
        except: pass    
        try: del member['sourceService']['refLink']
        except: pass  
        #need to look for ACL-name as well as same info could be in multiple acl's
        name = member['selfLink'].split('/')[6]    
        if member['destinationAddress'] == desired_data['destinationAddress'] and member['sourceAddress'] == desired_data['sourceAddress'] and member['destinationService'] == desired_data['destinationService'] and member['sourceService'] == desired_data['sourceService'] and member["permit"] == desired_data['permit']:
           objectId = member['objectId']
    try:
        result = dev.delete_acl(objectId, acl_name)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)

    if result.status_code == 204:
        return_status = True
    else:
        module.fail_json(msg='Unable to delete access-list entry - %s' % json.dumps(result.json(), sort_keys=True,indent=4, separators=(',', ': ')))

    return return_status

def find_member(current_data, desired_data, module):

    member_exists = False
    for member in current_data['items']:
        try: del member['destinationAddress']['refLink']
        except: pass
        try: del member['sourceAddress']['refLink']
        except: pass
        try: del member['destinationService']['refLink']
        except: pass    
        try: del member['sourceService']['refLink']
        except: pass        
        name = member['selfLink'].split('/')[6]      
        if member['destinationAddress'] == desired_data['destinationAddress'] and member['sourceAddress'] == desired_data['sourceAddress'] and member['destinationService'] == desired_data['destinationService'] and member['sourceService'] == desired_data['sourceService'] and member["permit"] == desired_data['permit']:
            member_exists = True
        #module.fail_json(msg="test %s %s %s" % (member_exists, json.dumps(desired_data, sort_keys=True,indent=4, separators=(',', ': ')), json.dumps(member, sort_keys=True,indent=4, separators=(',', ': '))))
    return member_exists


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            acl_name=dict(required=True),
            description=dict(required=False, default=''), #doesnt work yet
            permit=dict(required=False, defaut=True, type='bool'),
            protocol=dict(required=True),
            source_service=dict(required=False, default=None),
            source_address=dict(required=False, default='any4'),
            destination_service=dict(required=False, default=None),
            destination_address=dict(required=False, default='any4'),
            entry=dict(required=False, default=None),
            position=dict(required=False, default=1, type='str'),
            state=dict(required=True, choices=['absent', 'present']),
            validate_certs=dict(required=False, type='bool', default=False)),
        supports_check_mode=False)
    m_args = module.params 
    acl_name=m_args['acl_name']
    description=m_args['description']
    permit=m_args['permit']
    protocol=m_args['protocol']
    source_service=m_args['source_service']
    source_address=m_args['source_address']
    destination_service=m_args['destination_service']
    destination_address=m_args['destination_address']
    state = m_args['state']
    position=m_args['position']
    if isinstance(position, str):
        #module.fail_json(msg='hiyo %s %s' % (type(position), position))
        if position.lower() != 'last': 
            try: 
                position = int(position)
            except:
                pass
    dev = ASA(
        device=m_args['host'],
        username=m_args['username'],
        password=m_args['password'],
        verify_cert=m_args['validate_certs']
    )
    if m_args['entry']:  #need to do as try since some values may not be present
        entry = ast.literal_eval(m_args['entry'])  #had to do this for some reason in ansible 2.x as dict was read as string
        try:
            source_service=entry['source_service']
            if source_service in tcp_services.values():   #if well-known port name, convert to applicable int
                source_service = int(tcp_services.keys()[tcp_services.values().index(source_service)])
            elif source_service in udp_services.values():   #if well-known port name, convert to applicable int
                source_service = int(udp_services.keys()[udp_services.values().index(source_service)])
            elif source_service == 'www': source_service = '80'
            elif isinstance (source_service, str): #if the service is an integer represented as a string, convert to int
                if source_service.isdigit():
                    source_service = int(source_service)
        except:
            pass
        try:
            source_address=entry['source_address']
        except:
            pass
        try:
            destination_service=entry['destination_service']
            if destination_service in tcp_services.values():  #if well-known port name, convert to applicable int
                destination_service = int(tcp_services.keys()[tcp_services.values().index(destination_service)])
            elif destination_service in udp_services.values():  #if well-known port name, convert to applicable int
                destination_service = int(udp_services.keys()[udp_services.values().index(destination_service)])
            elif destination_service == 'www': destination_service = '80'
            elif isinstance (destination_service, str): #if the service is an integer represented as a string, convert to int
                if destination_service.isdigit():
                    destination_service = int(destination_service)
        except:
            pass
        try:    
            destination_address=entry['destination_address']
        except:
            module.fail_json(msg='hiyo %s %s' % (entry, type(entry)))
            #pass

    source_address_object = 'value'
    destination_address_object = 'value'
    source_service_object = 'value'
    destination_service_object = 'value'
    if source_address == 'any': source_address = 'any4'
    if destination_address == 'any': destination_address = 'any4'
#set the protocol and service paramerters
    if protocol == 'icmp':
        destination_service_kind = 'NetworkProtocol'
        source_service_kind = 'NetworkProtocol'
        destination_service_value = 'icmp'
        source_service_value = 'icmp'
        if isinstance(destination_service, int):
            destination_service_value = protocol + '/' + str(destination_service)
        elif isinstance(destination_service, str):
            destination_service_value = destination_service
            destination_service_kind = "objectRef#ICMPServiceGroup"
            destination_service_object = 'objectId'
    if protocol == 'ip':
        destination_service_kind = 'NetworkProtocol'
        source_service_kind = 'NetworkProtocol'
        destination_service_value = 'ip'
        source_service_value = 'ip'   
    elif protocol == 'tcp':
#if the protocol is TCP there are 4 options for the source, the service is a port number, range, object-group or none (any)     
        if isinstance(source_service, int):
            if str(source_service) in tcp_services.keys():
                source_service = tcp_services[str(source_service)]
            source_service_value = protocol + '/' + str(source_service)
            source_service_kind = 'TcpUdpService'
        elif source_service==None: 
#if there is no service passed to the module, use the base protocol
            source_service_value=protocol
            source_service_kind = 'NetworkProtocol' 
        else: #assumes a string
            if '--' in source_service: #if the value is a string representation of a port range
                port_range = string.split(source_service, "--")
                if port_range[0] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = tcp_services.keys()[tcp_services.values().index(port_range[0])]
                if port_range[1] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = tcp_services.keys()[tcp_services.values().index(port_range[1])]
                if 1 <= int(port_range[0]) <= 65535 and 1 <= int(port_range[1]) <= 65535 and int(port_range[0]) < int(port_range[1]):
                    source_service_value = protocol + "/" + port_range[0]+'-'+port_range[1]
                    source_service_kind = 'TcpUdpService'
                else:
                    module.fail_json(msg="%s is not a valid tcp port range" % value)           
            else: #assumes onbject-group
                source_service_value = source_service
                source_service_kind = "objectRef#TcpServiceGroup"
                source_service_object = 'objectId'
        if isinstance(destination_service, int):
        #module.fail_json(msg='yo %s %s' % (destination_service, tcp_services.keys()))
            if str(destination_service) in tcp_services.keys():
                destination_service = tcp_services[str(destination_service)]
            #module.fail_json(msg='yo %s' % destination_service)
            destination_service_value = protocol + '/' + str(destination_service)
            destination_service_kind = 'TcpUdpService'
        elif destination_service==None: 
#if there is no service passed to the module, use the base protocol
            destination_service_value=protocol
            destination_service_kind = 'NetworkProtocol'  
        else:
            if '--' in destination_service: #if the value is a string representation of a port range
                port_range = string.split(destination_service, "--")
                if port_range[0] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = tcp_services.keys()[tcp_services.values().index(port_range[0])]
                if port_range[1] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = tcp_services.keys()[tcp_services.values().index(port_range[1])]
                if 1 <= int(port_range[0]) <= 65535 and 1 <= int(port_range[1]) <= 65535 and int(port_range[0]) < int(port_range[1]):
                    destination_service_value = protocol + "/" + port_range[0]+'-'+port_range[1]
                    destination_service_kind = 'TcpUdpService'
                else:
                    module.fail_json(msg="%s is not a valid tcp port range" % value)           
            else: #assumes onbject-group
                destination_service_value = destination_service
                destination_service_kind = "objectRef#TcpServiceGroup"
                destination_service_object = 'objectId'
#if the protocol is UDP there are 4 options for dest, the service is a port number, range, object-group or none (any)
    elif protocol == 'udp':
        if isinstance(source_service, int):
            if str(source_service) in udp_services.keys():
                source_service = udp_services[str(source_service)]
            source_service_value = protocol + '/' + str(source_service)
            source_service_kind = 'TcpUdpService'
        elif source_service==None: 
#if there is no service passed to the module, use the base protocol
            source_service_value=protocol
            source_service_kind = 'NetworkProtocol' 
        else:
            if '--' in source_service: #if the value is a string representation of a port range
                port_range = string.split(source_service, "--")
                if port_range[0] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = udp_services.keys()[udp_services.values().index(port_range[0])]
                if port_range[1] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = udp_services.keys()[udp_services.values().index(port_range[1])]
                if 1 <= int(port_range[0]) <= 65535 and 1 <= int(port_range[1]) <= 65535 and int(port_range[0]) < int(port_range[1]):
                    source_service_value = protocol + "/" + port_range[0]+'-'+port_range[1]
                    source_service_kind = 'TcpUdpService'
            else: 
                source_service_value = source_service
                source_service_kind = "objectRef#UdpServiceGroup"
                source_service_value_object = 'objectId'
        if isinstance(destination_service, int):
            if str(destination_service) in udp_services.keys():
                destination_service = udp_services[str(destination_service)]
            destination_service_value = protocol + '/' + str(destination_service)
            destination_service_kind = 'TcpUdpService'
        elif destination_service==None: 
#if there is no service passed to the module, use the base protocol
            destination_service_value=protocol
            destination_service_kind = 'NetworkProtocol' 
        else:
            if '--' in destination_service: #if the value is a string representation of a port range
                port_range = string.split(destination_service, "--")
                if port_range[0] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = udp_services.keys()[udp_services.values().index(port_range[0])]
                if port_range[1] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = udp_services.keys()[udp_services.values().index(port_range[1])]
                if 1 <= int(port_range[0]) <= 65535 and 1 <= int(port_range[1]) <= 65535 and int(port_range[0]) < int(port_range[1]):
                    destination_service_value = protocol + "/" + port_range[0]+'-'+port_range[1]
                    destination_service_kind = 'TcpUdpService'
            else: 
                destination_service_value = destination_service
                destination_service_kind = 'objectRef#UdpServiceGroup'
                destination_service_object = 'objectId'
#Set the L3 addressing parameters
    if '/' in source_address: source_address_kind = 'IPv4Network'
    elif source_address == 'any4': source_address_kind = 'AnyIPAddress'
    elif '.' in source_address:  source_address_kind = 'IPv4Address'
    else: 
        source_address_kind = "objectRef#NetworkObjGroup"
        source_address_object = "objectId"
    if '/' in destination_address: destination_address_kind = 'IPv4Network'
    elif destination_address == 'any4': destination_address_kind = 'AnyIPAddress'
    elif '.' in destination_address:  destination_address_kind = 'IPv4Address'
    else: 
        destination_address_kind = "objectRef#NetworkObjGroup"
        destination_address_object = "objectId"
#build the json data to send in post
    desired_data = {
        "permit": permit,
        "position": position,
        "sourceAddress": {
            "kind": source_address_kind,
            source_address_object: source_address
        },
        "sourceService": {
            "kind": source_service_kind,
            source_service_object: source_service_value
        },
        "destinationAddress": {
            "kind": destination_address_kind,
            destination_address_object: destination_address
        },
        "remarks": [],
        "destinationService": {
            "kind": destination_service_kind,
            destination_service_object: destination_service_value
        },
    }
    if isinstance(position, str):
        if position.lower() == 'last':
            desired_data.pop("position")
    changed = False
    #new rasa style
    try:
        data = dev.get_acls(acl_name)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg='Unable to connect to device: %s' % err)
    #module.fail_json(msg='yo %s' % json.dumps(data.json(), sort_keys=True,indent=4, separators=(',', ': ')))
    if data.status_code == 200:
        found = find_member(data.json(), desired_data, module)
        #module.fail_json(msg="test %s %s %s" % (found, json.dumps(desired_data, sort_keys=True,indent=4, separators=(',', ': ')), json.dumps(data.json(), sort_keys=True,indent=4, separators=(',', ': '))))
        if found and m_args['state'] == 'present':
            changed_status = False
        elif found and m_args['state'] == 'absent':
            changed_status = delete_acl(dev, module, data.json(), desired_data, acl_name)
        elif m_args['state'] == 'present':
            changed_status = add_acl(dev, module, desired_data, acl_name)    
        elif m_args['state'] == 'absent':
            changed_status = False                    
        else:
           #Remove after members are implemented
           module.fail_json(msg='Unknown error check arguments') 
    elif data.status_code == 401:
        module.fail_json(msg='Authentication error')    
    elif data.status_code == 404:
        if m_args['state'] == 'absent':
            changed_status = False
        elif m_args['state'] == 'present':
            changed_status = add_acl(dev, module, desired_data, acl_name)
    else:
        module.fail_json(msg="Unsupported return code %s" % data.status_code)
    if changed == False:
        changed = changed_status
    return_msg = {}
    return_msg['changed'] = changed
    module.exit_json(**return_msg)


main()