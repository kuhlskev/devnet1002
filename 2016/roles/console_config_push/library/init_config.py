

class ConsoleClient(object):
    def __init__(self, module):
        self.module = module
        self.console_host = module.params['console_host']
        self.con_server_user = module.params['con_server_user']
        self.con_server_pass = module.params['con_server_pass']
        self.username = module.params['device_username']
        self.password = module.params['device_password']
        self.default_user = module.params['default_user']
        self.default_pass = module.params['default_pass']
        self.virl_port = module.params['virl_port']
        self.log = module.params['log']
        self.log_file = module.params['log_file']
        self.session = None
        self.logged_in = False

    def login(self):

            sesh = pexpect.spawn ('telnet {console_host} {virl_port}'.format(
                                   console_host=self.console_host, virl_port=self.virl_port))
            sesh.PROMPT = '\r\n.*#|\r\n.*>'
                                  
            for attempt in range(5):
                try:    
                    sesh.sendline('\r\n')
                    sleep(1)
                    i = sesh.expect(["(?i)login:", "(?i)username", "(?i)password:", sesh.PROMPT])
                    if i == 0 or i == 1:
                        sesh.sendline(self.username)
                        sleep(1)
                        sesh.sendline(self.password)
                        sesh.expect(sesh.PROMPT)
                    elif i == 2:
                        sesh.sendline(self.password)
                        sesh.expect(sesh.PROMPT)
                    elif i == 3:
                        self.logged_in = True
                        sesh.sendline("terminal length 0")
                        return True
                except (pxssh.ExceptionPxssh, pexpect.exceptions.TIMEOUT) as e:
                    sesh.close()
            
            else:
                sesh.close()
                self.module.fail_json(msg="Login Error: {}".format(e))
def main():
    module = AnsibleModule(
        argument_spec=dict(
#            console_host=dict(required=True, type='str'),
#            con_server_user=dict(required=True, type='str'),
#            con_server_pass=dict(required=True, no_log=True, type='str'),
#            device_username=dict(required=True, type='str'),
#            device_password=dict(required=True, no_log=True, type='str'),
#            default_user=dict(required=False, type='str', default='admin'),
#            default_pass=dict(required=False, no_log=True, type='str', default='admin'),
#            virl_port=dict(required=False, type='str', default=None),
#            log=dict(required=False, type='bool', default=False),
#            log_file=dict(required=False, type='str', default=None)
             console_host='10.10.10.156',
             virl_port='17000',
             device_username='cisco',
             device_password='cisco'

        )
    )
    #con = ConsoleClient(module)
    #con.login()
    candidate = NetworkConfig(contents='../templates/router_init.j2', indent=1)
    commands = str(candidate).split('\n')
    commands = [str(c).strip() for c in commands]
    #response = module.configure(commands)
    #routerHostname = "deep" #example - can be different
    #child.expect (routerHostname+'>')
    #child.sendline ('enable')
    #con.disconnect()
    module.exit_json(changed=False)

from ansible.module_utils.basic import *
from ansible.module_utils.shell import *
import pexpect
import getpass
from ansible.module_utils.netcfg import *
from ansible.module_utils.ios import *
if __name__ == '__main__':
    main()