import pexpect, sys, jinja2, yaml, commands, requests
from time import sleep
from ansible.module_utils.basic import *
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from ansible.module_utils.ios import *

username = 'cisco'
password = 'cisco'
enablepass = '\n'
#virl_ip = '10.10.10.156'
virl_ip = '198.18.134.1'
localhost = commands.getoutput("/sbin/ifconfig utun0").split('\n')[1].split()[1]
ftp_user = 'kekuhls'
ftp_password = "6yhn7ujm*IK<(OL>"
ftp_cmd = 'copy ftp://{ftp_user}:{ftp_password}@{localhost}/asa-restapi-121-lfbff-k8.SPA disk0:asa-restapi-121-lfbff-k8.SPA'.format(ftp_user=ftp_user,ftp_password=ftp_password,localhost=localhost)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}
roster_url = "http://{virl_ip}:19399/roster/rest/".format(virl_ip=virl_ip)
new_router = "Would you like to enter the initial configuration dialog?"

def build_dict():
    cred = requests.auth.HTTPBasicAuth('guest', 'guest')
    data = requests.get(roster_url, headers=HEADERS, auth=cred)
    data_dict = json.loads(data.text)
#need to find the ip and port info for devices, PortConsole is only in devices and mgmt int
#still need the interface to configure the ip for management
    device_info = {}
    for item, vals in data_dict.items():
        if "PortConsole" in vals:
            name = item.split('|')[-1]
            mgmt_ip = data_dict[item]['externalAddr']
            console_port = data_dict[item]['PortConsole']
            search = str(name) + ' interface'
            for key in data_dict:
                if search in key:
                    mgmt_int = data_dict[key]['Annotation'] 
            device_info.update({name: {'hostname': name, 'mgmt_ip':mgmt_ip, 
                               'console_port':console_port, 'mgmt_int': mgmt_int}})
    return device_info
    
def init_cfg(commands, data):
    x = 0
    for x in range (5):
        try:
            sesh = pexpect.spawn ('telnet {console_host} {virl_port}'.format(console_host=virl_ip, virl_port=data['console_port']))
            print virl_ip, data['console_port']            
            sesh.logfile = sys.stdout
            sesh.PROMPT = '\r\n.*#|\r\n.*>'                             
            sesh.sendline('\n\n\n')    
            sesh.expect('Connected to ')
            sleep(1)
            sesh.sendline('\n\n\n')
            sleep(1)
            if "x" in data['hostname']:
                sesh.expect(["Username", "login"])
                sesh.sendline('admin')
                sesh.expect('Password')
                sesh.sendline('admin')
                sleep(3)
                sesh.expect('#')
            i = sesh.expect(["(?i)login:", "(?i)username", "(?i)password:", 
                             "ciscoasa>", sesh.PROMPT, new_router])
            if i == 5:
                sesh.sendline('no\n\n')
                sesh.expect("Press RETURN to get started!")
                sesh.sendline('\n\n')
                #sleep(5)
                sesh.expect('Router>')
            if i == 3:
                logged_in = True
                x = 1
                print "good"
            if i == 0 or i == 1:
                sesh.sendline(username)
                sleep(1)
                sesh.sendline(password)
                sesh.expect(sesh.PROMPT)
            elif i == 2:
                sesh.sendline(password)
                sesh.expect(sesh.PROMPT)
            elif i == 4:
                logged_in = True
                sesh.sendline("terminal length 0")
                break
        except: 
            sesh.close()
    
    sesh.sendline ('enable\n')
    sesh.expect(sesh.PROMPT)
    sesh.sendline (enablepass)
    sesh.expect(sesh.PROMPT)
    sesh.sendline ('conf t\n')
    sesh.expect(sesh.PROMPT)
    for cmd in commands:
        sesh.sendline(cmd + '\n')
        sesh.expect(sesh.PROMPT)
    if "asa" in data['hostname']:
        sesh.sendline(ftp_cmd + '\n')
        sesh.sendline('\n')
        sesh.sendline('\n')
        sesh.sendline('\n')
        sesh.sendline('\n')
        sesh.sendline('\n')
        sesh.expect(sesh.PROMPT)
        sesh.sendline('rest-api image disk0:asa-restapi-121-lfbff-k8.SPA\n')
        sleep(35)
        sesh.expect(sesh.PROMPT) 
        sesh.sendline('rest-api agent\n')
        sesh.expect(sesh.PROMPT)                     
    sesh.close()

def main():

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='../templates/'))
   # with open('../vars/main.yml', "r") as file_descsriptor:
   #     data = yaml.load(file_descsriptor)
    data = build_dict()
    
    for item in data:
        if "asa" in item:
            template = env.get_template('asa_init.j2')
        elif "ios" in item:
            template = env.get_template('router_init.j2')
        elif "nxos" in item:
            template = env.get_template('nxos_init.j2')
        elif "xr" in item:
            template = env.get_template('xr_init.j2')
        init = template.render(data[item])
        commands = str(init).split('\n')    
        commands = [str(c).strip() for c in commands]
        print commands
        init_cfg(commands, data[item])
    with open('pod_info', 'w') as outfile:
        outfile.write( yaml.dump(data, default_flow_style=False) )    
    #module.exit_json(changed=False)

if __name__ == '__main__':
    main()