#!/bin/bash

case "$1" in

1) echo "ansible-playbook ios_example.yaml -i inventory"
   ansible-playbook ios_example.yaml -i inventory
   ;;

2) echo "ansible-playbook linux.yaml -i inventory"
   ansible-playbook linux.yaml -i inventory
   ;;

3) echo "ansible-playbook nc_example.yaml -i inventory"
   ansible-playbook nc_example.yaml -i inventory
   ;;

4) echo "ansible-playbook nxos.yaml -i inventory"
   ansible-playbook nxos.yaml -i inventory
   ;;

5) echo "ansible-playbook aci.yaml -i inventory"
   ansible-playbook aci.yaml -i inventory
   ;;

6) echo "ansible-playbook ucs.yaml -i inventory"
   ansible-playbook ucs.yaml -i inventory
   ;;

7) echo "ansible-playbook iac.yaml -i inventory"
   ansible-playbook iac.yaml -i inventory
   ;;

esac
