#!/bin/bash

case "$1" in

1) echo "ansible-playbook ios_25.yaml -i inventory"
   ansible-playbook ios_25.yaml -i inventory
   ;;

2) echo "ansible-playbook ios_template.yaml"
   ansible-playbook ios_template.yaml
   ;;   

3) echo "ansible-playbook nxos.yaml"
   ansible-playbook nxos.yaml
   ;;

4) echo "ansible-playbook nc_example.yaml"
   ansible-playbook nc_example.yaml
   ;;

5) echo "ansible-playbook nxos_25.yaml"
   ansible-playbook nxos_25.yaml
   ;;

6) echo "ansible-playbook iac.yaml"
   ansible-playbook iac.yaml
   ;;
   
esac
