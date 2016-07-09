#!/bin/bash

case "$1" in

1) echo "ansible-playbook ios_example.yaml -i inventory"
   ansible-playbook ios_example.yaml -i inventory
   ;;

2) echo "ansible-playbook ios_template.yaml -i inventory --skip-tags deploy"
   ansible-playbook ios_template.yaml -i inventory --skip-tags deploy
   ;;

3) echo "ansible-playbook ios_template.yaml -i inventory"
   ansible-playbook ios_template.yaml -i inventory
   ;;

4) echo "ansible-playbook asa_infra_as_code.yml -i inventory -M ansible-cisco-asa/library/"
   ansible-playbook asa_infra_as_code.yml -i inventory -M ansible-cisco-asa/library/
   ;;

esac