
#!/usr/bin/env python
import pexpect
from pexpect import pxssh
from time import sleep

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

    def create_session(self):
        try:
            sesh = pxssh.pxssh(options={
                               "StrictHostKeyChecking": "no",
                               "UserKnownHostsFile": "/dev/null"})
            # Enable the following line if you need to see all output.
            # This will make Ansible think that there was an error, however.
            #sesh.logfile_read = sys.stdout
            if self.log:
                # To only capture output (and not passwords) change logfile to logfile_read
                sesh.logfile = file(self.log_file, 'w')
            sesh.force_password = True
            return sesh

        except (pxssh.ExceptionPxssh, pexpect.ExceptionPexpect) as e:
            self.module.fail_json(msg="Connection Error: {}".format(e))

    def login(self):
        try:
            # Session must be initialized before being created
            self.session = None
            sesh = self.session = self.create_session()
            sesh.login(self.console_host, self.con_server_user, self.con_server_pass,
                       auto_prompt_reset=False, login_timeout=90)
            sesh.PROMPT = '\r\n.*#|\r\n.*>'
            sesh.sendline('\r\n')

            if self.virl_port:
                sesh.sendline('telnet {console_host} {virl_port}'.format(console_host=self.console_host, virl_port=self.virl_port))

        except (pxssh.ExceptionPxssh, pexpect.exceptions.TIMEOUT) as e:
            self.module.fail_json(msg="Connection Error: {}".format(e))

        except pexpect.exceptions.EOF as eof:
            self.module.fail_json(msg="Connection Error: Is {} reachable from this computer?".format(self.console_host))

        for attempt in range(5):
            try:
                # After login, send enter to show prompt
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

            # If the login fails, catch the exception and retry again
            except (pxssh.ExceptionPxssh, pexpect.exceptions.TIMEOUT) as e:
                sesh.close()

        # If all retries fail, error out
        else:
            sesh.close()
            self.module.fail_json(msg="Login Error: {}".format(e))


    def version(self):
        sesh = self.session
        sesh.sendline('show version')
        sesh.expect('Configuration register')
        return sesh.before

    def disconnect(self):
        # Cannot use logout() since this is a console. Manually disconnect
        self.session.sendline('exit')
        self.session.close()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            console_host=dict(required=True, type='str'),
            con_server_user=dict(required=True, type='str'),
            con_server_pass=dict(required=True, no_log=True, type='str'),
            device_username=dict(required=True, type='str'),
            device_password=dict(required=True, no_log=True, type='str'),
            default_user=dict(required=False, type='str', default='admin'),
            default_pass=dict(required=False, no_log=True, type='str', default='admin'),
            virl_port=dict(required=False, type='str', default=None),
            log=dict(required=False, type='bool', default=False),
            log_file=dict(required=False, type='str', default=None)
        )
    )
    con = ConsoleClient(module)
    con.login()
    con.disconnect()
    module.exit_json(changed=False)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
