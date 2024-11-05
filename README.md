# ansible-server

Ansible tool for managing devices

## Features

- [x] Playbooks for setting up an APT repository
- [x] Inventory plugin for discovering devices using SSDP

## Requirements

- [Python3](https://www.python.org/downloads/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## Running Ansible playbooks

### Using a static inventory file

1. Copy the inventory template file
    ```commandline
    cp inventories/edge-devices-template.ini inventories/edge-devices.ini
    ```
2. Add the list of hosts to the inventory file
    ```
    [all:vars]
    ansible_connection=ssh
    ansible_user=admin
    ansible_ssh_pass=admin
    [edge_devices]
    er-multi-b7b8bf51 ansible_host=er-multi-b7b8bf51.local
    er-multi-21b38357 ansible_host=er-multi-21b38357.local
    ```
3. Run the selected playbook on the inventory
    ```commandline
    ansible-playbook -i inventories/edge-devices.ini playbooks/setup-apt-repo-playbook.yaml
    ```

### Using an inventory plugin

1. Set up the inventory plugin directory
    ```commandline
    export ANSIBLE_INVENTORY_PLUGINS=$(pwd)/plugin
    ```
2. Run the selected playbook on the inventory with the default configuration file `configuration/ssdpPlugin.json`
    ```commandline
   ansible-playbook playbooks/setup-apt-repo-playbook.yaml
    ```
   or specify a custom configuration file
    ```commandline
   ansible-playbook playbooks/setup-apt-repo-playbook.yaml -i path/to/config.json
    ```
