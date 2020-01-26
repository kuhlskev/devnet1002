Start the lab (vagrant VMs and docker container with Ansible) with setup.sh.

Stop the lab with stop.sh

Delete the lab with cleanup.sh

The ansible playbooks are numbered 1_ through 5_ and are to be ran with ansible-playbook. 

Note:

To change the default config of the virtual router or switch, edit the conf file stored in the .iso, and then remake the iso. For example for the switch:

mkisofs -output nxosconfig.iso -l --relaxed-filenames --iso-level 2 NXOS_CONFIG.TXT
