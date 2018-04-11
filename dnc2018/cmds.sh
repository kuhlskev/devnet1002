#!/bin/bash

case "$1" in

1) echo "ansible-playbook ios_25.yaml -i inventory"
   ansible-playbook ios_25.yaml -i inventory
   ;;

2) echo "ansible-playbook linux.yaml"
   ansible-playbook linux.yaml
   ;;

3) echo "ansible-playbook ios_template.yaml"
   ansible-playbook ios_template.yaml
   ;;   

4) echo "ansible-playbook nxos.yaml"
   ansible-playbook nxos.yaml
   ;;

5) echo "ansible-playbook aci.yaml"
   ansible-playbook aci.yaml
   ;;

6) echo "ansible-playbook ucs.yaml"
   ansible-playbook ucs.yaml
   ;;

7) echo "ansible-playbook nc_example.yaml"
   ansible-playbook nc_example.yaml
   ;;

8) echo "ansible-playbook nxos_25.yaml"
   ansible-playbook nxos_25.yaml
   ;;

9) echo "ansible-playbook iac.yaml"
   ansible-playbook iac.yaml
   ;;

vpn) echo "ansible-playbook vpn.yaml"
   ansible-playbook vpn.yaml
   ;;

ucs) echo "ansible-playbook ucsmsdk.yaml"
   ansible-playbook ucsmsdk.yaml
   ;;

pip) echo "pip install --upgrade ansible xlrd xmltodict netaddr"
   pip install --upgrade ansible xlrd xmltodict netaddr 
   ;;
   
esac
