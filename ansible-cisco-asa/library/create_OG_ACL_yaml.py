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

'''This script can create a YAML file to represent the configuration of an ASA
The YAML can be consumed by an ansible playbook similar to the example-cisco_asa_infra_as_code.yml 
'''

import yaml
import iptools
from netaddr import IPNetwork, IPAddress
import socket, struct
from jinja2 import Environment, FileSystemLoader
import re

#Please update the following for the desired filenames
asa_config_file = 'asa-config-file'
yaml_asa_representation = 'yaml-file-output.yml'

if __name__ == "__main__":
 f = open(asa-config-file, 'r')
 whole_file = f.readlines()
 og_acl_dict = {}
 static_routes = []
 svc_object_groups = []
 net_object_groups = []
 access_lists = []
 net_count = 0
 svc_count = 0
 acl_count = 0
 acl = []
 ipv4pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

 for line in whole_file:
    if 'remark' in line:
        print (line)
    elif 'route ' in line:
        route_entry = {}
        entry= line.split(' ')
        print (entry.count(''))
        for x in range(0,entry.count('')): 
            entry.remove('')
        route_entry['interface'] = entry[1]
        prefix = str(iptools.ipv4.netmask2prefix(entry[3]))
        if '{' in entry[3]: prefix = entry[3]
        route_entry['network'] = entry[2] + '/' + prefix
        route_entry['next_hop'] = entry[4]
        static_routes.insert(0,route_entry)
    elif 'object-group' in line[0:20]:
    #get object-group name from object-group network|service object_name
        og_entry = {}
        entry = line.split(' ')
        name = entry[2].strip('\n')
        #print(name)
        if entry[1] == 'network':
            net_object_groups.insert(net_count,{'name':name})
            net_object_groups[net_count]['values'] = []
            net_count = net_count + 1
            toggle = 'network'
        if entry[1] == 'service':
            svc_object_groups.insert(svc_count,{'name':name})
            svc_object_groups[svc_count]['protocol'] = entry[3].strip('\n') 
            svc_object_groups[svc_count]['values'] = []
            svc_count = svc_count + 1
            toggle = 'service'
        if entry[1] == 'icmp-type':
            svc_object_groups.insert(svc_count,{'name':name})
            svc_object_groups[svc_count]['protocol'] = 'icmp' 
            svc_object_groups[svc_count]['values'] = []
            svc_count = svc_count + 1
        count = 0
    elif 'network-object' in line:
        #get object-group contents
        entry = line.split(' ')
        index = entry.index('network-object')
        if entry [index + 1] == 'host':
            # if a host network object-group
            net_object_groups[net_count - 1]['values'].insert(count,entry[index+2].strip('\n'))       
        else:   #must be network statement in object group
            prefix = iptools.ipv4.netmask2prefix(entry[index+2].strip('\n'))
            if '{' in entry[index+1]:
                mask_var = entry[index+2].strip('\n')
                mask_var_split = mask_var.split('_')
                prefix = mask_var_split[0]+'_prefixlen}}'
            net_object_groups[net_count - 1]['values'].insert(count,entry[index+1]+'/'+str(prefix))
        count = count + 1
    elif 'group-object' in line: #object-group entry must be group
        entry = line.split(' ')
        index = entry.index('group-object')
        if toggle == 'network':
            net_object_groups[net_count - 1]['values'].insert(count,entry[index+1].strip('\n'))
        if toggle == 'service':
            svc_object_groups[svc_count - 1]['values'].insert(count,entry[index+1].strip('\n'))
        count = count + 1
    elif 'port-object' in line:
        entry = line.split(' ')
        index = entry.index('port-object')
        if 'eq' == entry[index+1]:
            svc_object_groups[svc_count - 1]['values'].insert(count,entry[index+2].strip('\n'))
        else: 
            svc_object_groups[svc_count - 1]['values'].insert(count,entry[index+2]+'--'+entry[index+3].strip('\n'))
        count = count + 1
    elif 'icmp-object' in line:
        entry = line.split(' ')
        index = entry.index('icmp-object')
        svc_object_groups[svc_count - 1]['values'].insert(count,entry[index+1].strip('\n'))
        count = count + 1
    elif 'access-list' in line[0:15]: #make a list of acl lines to put the list in backward in yaml to allow for deny lines
        src_dest= {}
        acl_entry = {}
        line = line.strip('\n')
        entry = line.split(' ')
        index = entry.index('access-list')
        entry = entry[index+1::]
        name = entry.pop(0)
        if entry [0] == 'extended': entry.pop(0) #pop off 'extended'
        permit  = entry.pop(0) == 'permit'
        protocol = entry.pop(0)
        #get the source IP info
        if entry[0] == 'object-group':
            entry.pop(0)
            src_dest['source_address']= entry.pop(0)
        elif entry[0] == 'any':
            src_dest['source_address']= entry.pop(0)
        elif entry[0] == 'host' :
            entry.pop(0)
            src_dest['source_address']= entry.pop(0)
        elif ipv4pattern.match(entry[0]):
            src_dest['source_address']= entry.pop(0) + '/' + str(iptools.ipv4.netmask2prefix(entry.pop(0)))
        #get the source service info
        if entry [0] == 'eq':
            entry.pop(0)
            src_dest['source_service'] = entry.pop(0)
        elif entry [0] == 'range':
            entry.pop(0)
            src_dest['source_service'] = entry.pop(0)+'--'+entry.pop(0)
        elif entry[0] == 'object-group':
            if any(d['name'] == entry[1] for d in svc_object_groups): #if the object-group name is a service object-group
                entry.pop(0)
                src_dest['source_service'] = entry.pop(0)
        #get the desination ip info
        if entry[0] == 'object-group':
            entry.pop(0)
            src_dest['destination_address']= entry.pop(0)
        elif entry[0] == 'any':
            src_dest['destination_address']= entry.pop(0)
        elif entry[0] == 'host' :
            entry.pop(0)
            src_dest['destination_address']= entry.pop(0)
        elif ipv4pattern.match(entry[0]): 
            src_dest['destination_address']= entry.pop(0) + '/' + str(iptools.ipv4.netmask2prefix(entry.pop(0)))
        #get the destination service info
        if entry != []:
            if entry [0] == 'eq':
                entry.pop(0)
                src_dest['destination_service'] = entry.pop(0)
            elif entry [0] == 'range':
                entry.pop(0)
                src_dest['destination_service'] = entry.pop(0)+'--'+entry.pop(0)
            elif entry[0] == 'object-group':
                entry.pop(0)
                src_dest['destination_service'] = entry.pop(0)        
        #make the acl yaml
        acl_entry.update({'name':name, 'permit':permit, 'protocol':protocol, 'entry':src_dest})
        print(src_dest)
        access_lists.insert(0,acl_entry)
    og_acl_dict.update({'net_object_groups':net_object_groups,'svc_object_groups':svc_object_groups, 'access_lists':access_lists, 'static_routes':static_routes})
 with open(yaml_asa_representation, 'w') as outfile:
    outfile.write( yaml.dump(og_acl_dict, default_flow_style=False) )





     


