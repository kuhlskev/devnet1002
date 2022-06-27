# Ansible and APIs

## Enable APIs via Ansible Roles

```bash
ansible-playbook -i inventory 30_api_enable.yaml
```

## NETCONF IOS XE Example:

```bash
ansible-playbook -i inventory 40_netconf.yaml 
```

## NX-OS NX-API Example:

```bash
ansible-playbook -i inventory 50_nxos.yaml 
```