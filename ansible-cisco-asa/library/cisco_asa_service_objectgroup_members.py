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

DOCUMENTATION = """
---

module: cisco_asa_network_objectgroup
author: Kevin Kuhls - borrowed largely from Patrick Ogenstad (@networklore)
version: 1.0
short_description: Creates deletes or edits network object-groups.
description:
    - Configures service object-groups
requirements:
    - rasa
options:
    category:
        description:
            - The type of object you are creating. Use slash notation for networks, i.e. 192.168.0.0/24. Use - for ranges, i.e. 192.168.0.1-192.168.0.10. 
        choices: [ "ipv4_address", "ipv6_address", "ipv4_subnet", "ipv6_subnet", "ipv4_range", "ipv6_range", "ipv4_fqdn", "ipv6_fqdn", "object", "object_group" ]
        required: false
    description:
        description:
            - Description of the object
        required: false
    entry_state:
        description:
            - State of the object-group entry
        choices: [ "present", "absent" ]
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
        choices: [ "present", "absent" ]
        required: true
    username:
        description:
            - Username for device
        required: true
    validate_certs:
        description:
            - If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
        choices: [ "no", "yes"]
        default: "yes"
        required: false
    value:
        description:
            - The data to enter into the network object
        required: false

"""

EXAMPLES = """

# Create a network object for a web server
- cisco_asa_network_object:
    host={{ inventory_hostname }}
    username=api_user
    password=APIpass123
    name=tsrv-web-1
    state=present
    category=IPv4Address
    description="Test web server"
    value="10.12.30.10"
    validate_certs=no

# Remove test webserver
- cisco_asa_network_object:
    host={{ inventory_hostname }}
    username=api_user
    password=APIpass123
    name=tsrv-web-2
    state=absent
    validate_certs=no
"""

import re
import json
import sys
import string
from ansible.module_utils.basic import *
from collections import defaultdict
import requests
from requests import Request
from requests.auth import HTTPBasicAuth
#requests.packages.urllib3.disable_warnings()

ipv4pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
#    "User-Agent": "RASA"
}
ip_protocol_name = {
    "0": "ip",
    "1": "icmp",
    "2": "igmp",
    "3": "3",
    "4": "ipinip",
    "5": "5",
    "6": "tcp",
    "7": "7",
    "8": "8",
    "9": "igrp",
    "10": "10",
    "11": "11",
    "12": "12",
    "13": "13",
    "14": "14",
    "15": "15",
    "16": "16",
    "17": "udp",
    "18": "18",
    "19": "19",
    "20": "20",
    "21": "21",
    "22": "22",
    "23": "23",
    "24": "24",
    "25": "25",
    "26": "26",
    "27": "27",
    "28": "28",
    "29": "29",
    "30": "30",
    "31": "31",
    "32": "32",
    "33": "33",
    "34": "34",
    "35": "35",
    "36": "36",
    "37": "37",
    "38": "38",
    "39": "39",
    "40": "40",
    "41": "41",
    "42": "42",
    "43": "43",
    "44": "44",
    "45": "45",
    "46": "46",
    "47": "47",
    "48": "48",
    "49": "49",
    "50": "esp",
    "51": "ah",
    "52": "52",
    "53": "53",
    "54": "54",
    "55": "55",
    "56": "56",
    "57": "57",
    "58": "icmp6",
    "59": "59",
    "60": "60",
    "61": "61",
    "62": "62",
    "63": "63",
    "64": "64",
    "65": "65",
    "66": "66",
    "67": "67",
    "68": "68",
    "69": "69",
    "70": "70",
    "71": "71",
    "72": "72",
    "73": "73",
    "74": "74",
    "75": "75",
    "76": "76",
    "77": "77",
    "78": "78",
    "79": "79",
    "80": "80",
    "81": "81",
    "82": "82",
    "83": "83",
    "84": "84",
    "85": "85",
    "86": "86",
    "87": "87",
    "88": "eigrp",
    "89": "ospf",
    "90": "90",
    "91": "91",
    "92": "92",
    "93": "93",
    "94": "nos",
    "95": "95",
    "96": "96",
    "97": "97",
    "98": "98",
    "99": "99",
    "100": "100",
    "101": "101",
    "102": "102",
    "103": "pim",
    "104": "104",
    "105": "105",
    "106": "106",
    "107": "107",
    "108": "pcp",
    "109": "snp",
    "110": "110",
    "111": "111",
    "112": "112",
    "113": "113",
    "114": "114",
    "115": "115",
    "116": "116",
    "117": "117",
    "118": "118",
    "119": "119",
    "120": "120",
    "121": "121",
    "122": "122",
    "123": "123",
    "124": "124",
    "125": "125",
    "126": "126",
    "127": "127",
    "128": "128",
    "129": "129",
    "130": "130",
    "131": "131",
    "132": "132",
    "133": "133",
    "134": "134",
    "135": "135",
    "136": "136",
    "137": "137",
    "138": "138",
    "139": "139",
    "140": "140",
    "141": "141",
    "142": "142",
    "143": "143",
    "144": "144",
    "145": "145",
    "146": "146",
    "147": "147",
    "148": "148",
    "149": "149",
    "150": "150",
    "151": "151",
    "152": "152",
    "153": "153",
    "154": "154",
    "155": "155",
    "156": "156",
    "157": "157",
    "158": "158",
    "159": "159",
    "160": "160",
    "161": "161",
    "162": "162",
    "163": "163",
    "164": "164",
    "165": "165",
    "166": "166",
    "167": "167",
    "168": "168",
    "169": "169",
    "170": "170",
    "171": "171",
    "172": "172",
    "173": "173",
    "174": "174",
    "175": "175",
    "176": "176",
    "177": "177",
    "178": "178",
    "179": "179",
    "180": "180",
    "181": "181",
    "182": "182",
    "183": "183",
    "184": "184",
    "185": "185",
    "186": "186",
    "187": "187",
    "188": "188",
    "189": "189",
    "190": "190",
    "191": "191",
    "192": "192",
    "193": "193",
    "194": "194",
    "195": "195",
    "196": "196",
    "197": "197",
    "198": "198",
    "199": "199",
    "200": "200",
    "201": "201",
    "202": "202",
    "203": "203",
    "204": "204",
    "205": "205",
    "206": "206",
    "207": "207",
    "208": "208",
    "209": "209",
    "210": "210",
    "211": "211",
    "212": "212",
    "213": "213",
    "214": "214",
    "215": "215",
    "216": "216",
    "217": "217",
    "218": "218",
    "219": "219",
    "220": "220",
    "221": "221",
    "222": "222",
    "223": "223",
    "224": "224",
    "225": "225",
    "226": "226",
    "227": "227",
    "228": "228",
    "229": "229",
    "230": "230",
    "231": "231",
    "232": "232",
    "233": "233",
    "234": "234",
    "235": "235",
    "236": "236",
    "237": "237",
    "238": "238",
    "239": "239",
    "240": "240",
    "241": "241",
    "242": "242",
    "243": "243",
    "244": "244",
    "245": "245",
    "246": "246",
    "247": "247",
    "248": "248",
    "249": "249",
    "250": "250",
    "251": "251",
    "252": "252",
    "253": "253",
    "254": "tcp-udp",
    "255": "255"
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
        url = "https://" + self.device + "/api/" + request
        data = requests.delete(url,headers=HEADERS,auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _get(self, request):
        url = "https://" + self.device + "/api/" + request
        data = requests.get(url, headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _patch(self, request, data):
        url = "https://" + self.device + "/api/" + request
        data = requests.patch(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    def _post(self, request, data=False):
        url = "https://" + self.device + "/api/" + request
        if data != False:
            data = requests.post(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        else:
            data = requests.post(url, headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)            
        return data

    def _put(self, request, data):
        url = "https://" + self.device + "/api/" + request
        data = requests.put(url, data=json.dumps(data), headers=HEADERS, auth=self.cred, verify=self.verify_cert, timeout=self.timeout)
        return data

    ######################################################################
    # Unsorted functions
    ######################################################################
    def get_access_in(self):
        request = "access/in"
        return self._get(request)

    def get_acl_ace(self, acl):
        request = "objects/extendedacls/" + acl + "/aces"
        return self._get(request)

    def get_acls(self):
        request = "objects/extendedacls"
        return self._get(request)

    def get_localusers(self):
        request = "objects/localusers"
        return self._get(request)

 
    ######################################################################
    # Functions related to network object-groups, or
    # "object-group network" in the ASA configuration
    ######################################################################

    def add_member_networkservicegroup(self, svc_object, member_data):
        request = "objects/networkservicegroups/" + svc_object
        data = {}
        data["members.add"] = [member_data]
        return self._patch(request, data)

    def create_networkservicegroup(self, data):
        request = "objects/networkservicegroups"
        return self._post(request, data)

    def delete_networkservicegroup(self, svc_object):
        request = "objects/networkservicegroups/" + svc_object
        return self._delete(request)

    def get_networkservicegroup(self, svc_object):
        request = "objects/networkservicegroups/" + svc_object
        return self._get(request)

    #def get_networkservicegroup(self):
    #    request = "objects/networkservicegroup"
    #    return self._get(request)

    def remove_member_networkservicegroup(self, svc_object, member_data):
        request = "objects/networkservicegroups/" + svc_object
        data = {}
        data["members.remove"] = member_data
        return self._patch(request, data)

    def update_networkservicegroup(self, svc_object, data):
        request = "objects/networkservicegroups/" + svc_object
        return self._patch(request, data)

    def write_mem(self):
        """Saves the running configuration to memory
        """
        request = "commands/writemem"
        return self._post(request)

################################################################
def add_object(dev, module, svc_object, member_data):
    patch_data = {}
    patch_data["members.add"] = [member_data]
    #module.fail_json(msg="object - %s" % patch_data)
    try:
        result = dev.add_member_networkservicegroup(svc_object,member_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code != 204:
        module.fail_json(msg="Unable to add object - %s" % patch_data)

    return True


def create_object(dev, module, desired_data):
    try:
        result = dev.create_networkservicegroup(desired_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code == 201:
        return_status = True
    else:
        module.fail_json(msg="Unable to create object - %s" % desired_data)

    return return_status

def delete_object(dev, module, name):
    try:
        result = dev.delete_networkservicegroup(name)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code == 204:
        return_status = True
    else:
        module.fail_json(msg="Unable to delete object - %s" % result.status_code)

    return return_status

def find_member(current_data, desired_data, module):

    member_exists = False
    for member in current_data["members"]:
        if member == desired_data:
            member_exists = True

    return member_exists

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            name=dict(required=True),
            entry_state=dict(required=False, choices=["absent", "present"], default="present"),
            description=dict(required=False),
            state=dict(required=False, choices=["absent", "present"], default="present"),
            protocol=dict(required=True, choices=["tcp", "udp", "tcp-udp", "icmp"]),  
            members=dict(required=False, type ="list", default=[]),       
            validate_certs=dict(required=False, type="bool", default=False),
            value=dict(required=False, default='Empty')
            ),
        supports_check_mode=False)

    m_args = module.params

    #if not has_rasa:
    #    module.fail_json(msg="Missing required rasa module (check docs)")

    if m_args["state"] == "present":
        if m_args["protocol"] == False:
            module.fail_json(msg="Protocol not defined")

    dev = ASA(
        device=m_args["host"],
        username=m_args["username"],
        password=m_args["password"],
        verify_cert=m_args["validate_certs"]
    )
    
    device=m_args["host"],
    username=m_args["username"],
    password=m_args["password"],
    verify_cert=m_args["validate_certs"]
    #module.fail_json(msg="%s HUH?" % m_args['value'])
    members = []
    if m_args['members'] == []:
        members.append(m_args["value"])
    else:
        x = 0
        for item in m_args['members']:
            members.append(m_args['members'][x])
            x = x+1
#Set Object kind and default member_kind to object references
    #if m_args["protocol"] == "tcp":
    #    kind = "object#TcpServiceGroup"
    #    member_kind = "objectRef#TcpServiceGroup"
    #elif m_args["protocol"] == "udp":
    #    kind = "object#UdpServiceGroup"
    #    member_kind = "objectRef#UdpServiceGroup"
    #else:
    #    kind = "object#TcpUdpServiceGroup"
    #    member_kind = "objectRef#TcpUdpServiceGroup"

    intpattern = re.compile("^[0-9]+")
    rangepattern = re.compile("^[0-9]+--[0-9]+$")
    changed = False
    for value in members:
        if m_args["protocol"] == "tcp":
            kind = "object#TcpServiceGroup"
            member_kind = "objectRef#TcpServiceGroup"
            if value in tcp_services.values():
                value = tcp_services.keys()[tcp_services.values().index(value)]
            if value == 'www': value = 80
        elif m_args["protocol"] == "udp":
            kind = "object#UdpServiceGroup"
            member_kind = "objectRef#UdpServiceGroup"
            if value in udp_services.values():
                value = udp_services.keys()[udp_services.values().index(value)]
        elif m_args["protocol"] == "icmp":
            kind = "object#ICMPServiceGroup"
            member_kind = "ICMPService"
        else:
            kind = "object#TcpUdpServiceGroup"
            member_kind = "objectRef#TcpUdpServiceGroup"        
        kind_type = "value"
        if isinstance(value, str):
            if '--' in value: #if the value is a string representation of a port range
                #module.fail_json(msg="%s this is what we got" % value)
                port_range = string.split(value, "--")
                if port_range[0] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = tcp_services.keys()[tcp_services.values().index(port_range[0])]
                elif port_range[0] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[0] = udp_services.keys()[udp_services.values().index(port_range[0])]
                if port_range[1] in tcp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = tcp_services.keys()[tcp_services.values().index(port_range[1])]
                elif port_range[1] in udp_services.values():   #if well-known port name, convert to applicable int
                    port_range[1] = udp_services.keys()[udp_services.values().index(port_range[1])]
                if 1 <= int(port_range[0]) <= 65535 and 1 <= int(port_range[1]) <= 65535 and int(port_range[0]) < int(port_range[1]):
                    member_kind = "TcpUdpService"
                    value = m_args["protocol"] + "/" + port_range[0]+'-'+port_range[1]
                else:
                    module.fail_json(msg="%s is not a valid tcp port range" % value)
            elif intpattern.match(value): #if the value is a string representation of a integer for port
                value = int(value)
            elif m_args["protocol"] == "icmp":
                value = m_args["protocol"] + "/" + value
            else:
                kind_type = "objectId"
        #if port number
        if isinstance(value, int):
                if 1 <= value <= 65535:
                    member_kind = "TcpUdpService"
                    #if the port is a well-known port that the ASA will replace with the service name
                    if m_args["protocol"] == "tcp" and str(value) in tcp_services:
                        value = tcp_services[str(value)]
                    if m_args["protocol"] == "udp" and str(value) in udp_services:
                        value = udp_services[str(value)]
                    value = m_args["protocol"] + "/" + str(value)
                else:
                    module.fail_json(msg="%s is not a valid tcp port" % value)
        #module.fail_json(msg="test - %s %s %s" % (value, kind, kind_type))    
        desired_data = {}
        desired_data["name"] = m_args["name"]
        desired_data["kind"] = kind
        if m_args["description"]:
            desired_data["description"] = m_args["description"]
        member_data = {}
        if m_args["entry_state"]:
            member_data["kind"] = member_kind
            if kind_type == "objectId":
                ref_link = "https://%s/api/objects/networkservicegroups/%s" % (m_args["host"], value)
                member_data["refLink"] = ref_link
                member_data["objectId"] = value
            else:
                member_data["value"] = value  
            desired_data["members"] = [member_data]
        data = {}
        data = dev.get_networkservicegroup(m_args["name"])
        if data.status_code == 200:
            if m_args["state"] == "absent":
                changed_status = delete_object(dev, module, m_args["name"])
            elif m_args["state"] == "present" and m_args["entry_state"]:
                change_description = False
                if m_args["description"]:
                    current_data = data.json()
                    try:
                        if m_args["description"] == current_data["description"]:
                            change_description = False
                        else:
                            change_description = True
                    except:
                        change_description = True
                found = find_member(data.json(), member_data, module)
                if found and m_args["entry_state"] == "present":
                    changed_status = False
                elif found and m_args["entry_state"] == "absent":
                    changed_status = remove_object(dev, module, m_args["name"], member_data)
                elif m_args["entry_state"] == "present":
                    #module.fail_json(msg="test - %s %s %s" % (value, kind, kind_type))    
                    changed_status = add_object(dev, module, m_args["name"], member_data)
                    patch_data = {}
                    patch_data["members.add"] = [member_data]
                elif m_args["entry_state"] == "absent":
                    changed_status = False                
                if change_description:
                    changed_status = modify_description(dev, module, m_args["name"],m_args["description"])
            #elif m_args["state"] == "present" and m_args["members"]:
            #    module.fail_json(msg="This feature is eagerly awaiting to be developed")
            else:
               #Remove after members are implemented
               module.fail_json(msg="Unknown error check arguments") 
        elif data.status_code == 401:
            module.fail_json(msg="Authentication error")
        elif data.status_code == 404:
            if m_args["state"] == "absent":
                changed_status = False
            elif m_args["state"] == "present":
                #module.fail_json(msg="test2 - %s %s %s" % (value, desired_data, kind_type))    
                changed_status = create_object(dev, module, desired_data)  
        else:
            module.fail_json(msg="Unsupported return code %s" % data.status_code)
        if changed == False:
            changed = changed_status
    return_msg = {}
    return_msg["changed"] = changed

    module.exit_json(**return_msg)

def modify_description(dev, module, svc_object, description):
    data = {}
    data["description"] = description
    try:
        result = dev.update_networkservicegroup(svc_object, data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code != 204:
        module.fail_json(msg="Unable to change description - %s" % result.status_code)

    return True
    
def remove_object(dev, module, svc_object, member_data):
    try:
        result = dev.remove_member_networkservicegroup(svc_object,[member_data])
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code != 204:
        module.fail_json(msg="Unable to remove object - %s" % result.status_code)

    return True

def update_object(dev, module, desired_data):
    try:
        result = dev.update_networkobject(desired_data["name"], desired_data)
    except:
        err = sys.exc_info()[0]
        module.fail_json(msg="Unable to connect to device: %s" % err)

    if result.status_code == 204:
        return_status = { "changed": True }
    else:
        module.fail_json(msg="Unable to update object code: - %s" % result.status_code)

    return return_status



main()

