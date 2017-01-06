#!/bin/bash

case "$1" in

1) echo "ansible-playbook ios_example.yaml -i inventory"
   ansible-playbook ios_example.yaml -i inventory
   ;;

2) echo "ansible-playbook ios_template.yaml -i inventory --skip-tags deploy"
   ansible-playbook ios_template.yaml -i inventory --skip-tags "deploy,xml_deploy"
   ;;

3) echo "ansible-playbook ios_template.yaml -i inventory"
   ansible-playbook ios_template.yaml -i inventory --skip-tags xml_deploy
   ;;

4) echo "ansible-playbook nc_example.yaml -i inventory"
   ansible-playbook nc_example.yaml -i inventory
   ;;

5) echo "ansible-playbook ios_template.yaml -i inventory --skip-tags depoy"
   ansible-playbook ios_template.yaml -i inventory --skip-tags depoy
   ;;


esac