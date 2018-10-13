# UFW-Ansible

An Ansible playbook that pushes UFW firewall rules to remote hosts.
Included is a python script that will generate the Ansible group/vars/ configuration files given two base files with port groups and port definitions.

## Getting Started

Install the Ansible playbook in /etc/ansible. Note that example files of all the configuration files needed are included.

## ufw-configure.yml

The Ansible playbook to be run. Note that you should change the line referincing Ansible Master's IP address to whatever your Ansible Master's IP address is. 

To run:

```
ansible-playbook -i hosts ufw-configure.yml
```

Note that you may need to set ```hash_behaviour = merge``` in ansible.cfg

## UFW-Generator.py

Script to generate the group/vars files that the Ansible playbook will parse. Port_Groups has a list of the Ansible host groups and the ports that are to be opened for each group of hosts. Port_Definitions has all of the port numbers and protocol definitions for the ports listed in Port_Groups. Both files must match, every port listed in Port_Groups must have a definition in Port_Definitions. Two example files have been provided. 
