## About

Repo containing [Ansible](https://github.com/ansible/ansible) modules for Cisco ASA using the REST API which appeared in ASA 9.3.

## Alpha code

Currently this is only a test and there's a good chance that a lot of the code will change.

## Dependencies

These modules requires:

* An ASA firewall running 9.3 or later

## Current modules

* cisco_asa_create_acl
* cisco_asa_service_objectgroup_members
* cisco_asa_network_objectgroup_members
* cisco_asa_route
* cisco_asa_cli
* cisco_asa_write_mem

## Installation of Ansible module

If you are running Ansible through a Python virtualenv you might need to change the ansible_python_interpreter variable. Check the hosts file in this repo for an example. You can clone this repo and copy the modules to your Ansible library path.

## Known issues

* Changing service object types doesn't work. I.e. changing an "object service" from tcp/udp/icmp to a network protocol.

## Feedback

If you have any questions or feedback. Please send me a note at kekuhls@cisco.com.

## How to run

You can edit a playbook and run all within the playbook (sample: sample_playbook.yml)
	ansible-playbook example-playbooks/how-to/sample_playbook.yml -i inventory -M library

or you can edit/create a yaml to consume into the playbook (sample: run asa-api.yml with input.yml)
	ansible-playbook example-playbooks/how-to/examples-cisco_asa_infra_as_code.yml -i hosts -M library

## Taking advantage of converting a current ASA config into yaml to be consumed by asa-api.yml
use the library/create_OG_ACL_yaml.py with the asa config file to convert to yaml and the name of the output file and run the script

