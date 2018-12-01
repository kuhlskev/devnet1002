#!/usr/bin/env python
import pexpect
import time
from ansible.module_utils.basic import *

def main():

    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            type=dict(choices=['show', 'config'], required=True),
            protocol=dict(required=True, choices=['ssh', 'telnet']),
            port=dict(required=False),
            username=dict(type='str'),
            password=dict(type='str'),
            enablepass=dict(type='str', required=False, defaul='\n'),
            fname=dict(type='str', required=True)
        ),
        supports_check_mode=False
    )
    m_args = module.params
    if m_args['protocol'] == 'telnet':
        child = pexpect.spawn ('telnet {host} {port}'.format(host=m_args['host'], port=m_args['port']))
    else:
        child = pexpect.spawn ('ssh {username}@{host}'.format(host=m_args['host'], username=m_args['username'] ))
    child.expect('password')
    child.sendline(m_args['password'])
    child.sendline ('\n\n')
#    child.expect ('>')
#    child.sendline ('enable\n')
#    child.expect('assword')
#    child.sendline(m_args['enablepass'])
    child.expect ('#')
    child.sendline('conf t')
    child.expect ('#')  
    with open(m_args['fname']) as infile:
        for line in infile:
            child.sendline (line)
            child.expect(['#','ERROR']) #need to figure out cmd error cases
            print (line)
    time.sleep (10) #why is this here?
    child.close()
if __name__ == '__main__':
    main()