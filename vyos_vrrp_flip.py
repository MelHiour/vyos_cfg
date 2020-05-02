import helpers
import click
import getpass
import re
from pprint import pprint

VRRP_REGEX = "set high-availability vrrp group (\w.*) priority '(\d.*)'"
COMMAND = 'show configuration commands | match "vrrp group.*priority"'

def parse_vrrp(raw_dictionary, vrrp_regex):
    parsed_vrrp_dict = {}
    pattern = re.compile(vrrp_regex)
    
    for device, config in raw_dictionary.items():
        parsed_vrrp_dict[device] = {}
        for line in config:
            if line.startswith('set'):
                result = pattern.findall(line)
                parsed_vrrp_dict[device][result[0][0]] = result[0][1]
    resulted_dict ={}
    for device, groups in parsed_vrrp_dict.items():
        priorities = set([priority for priority in groups.values()])
        if len(priorities) != 1:
            raise ValueError('VRRP priority is not consistence accoss the device')
        elif '200' in priorities:
            resulted_dict[device] = {}
            resulted_dict[device]['Master'] = True
            resulted_dict[device]['Groups'] = [group for group in groups.keys()]
        elif '100' in priorities:
            resulted_dict[device] = {}
            resulted_dict[device]['Master'] = False
            resulted_dict[device]['Groups'] = [group for group in groups.keys()]
        else:
            raise ValueError('VRRP priority value is not supported') 
    return resulted_dict

def generate_config(vrrp_device_dict):
    template = "set high-availability vrrp group {} priority {}"
    if vrrp_device_dict['Master'] == False:
        commands = [template.format(group, '200') for group in vrrp_device_dict['Groups']]
    elif vrrp_device_dict['Master'] == True:
        commands = [template.format(group, '100') for group in vrrp_device_dict['Groups']]
    return commands

def main(inventory, verbose):
    parsed_inventory = helpers.parse_yaml(inventory)
    password = getpass.getpass('Please enter a password: ')

    configs = {}
    for device, params in parsed_inventory.items():
        params['password'] = password
        config = helpers.run_show(params, COMMAND, verbose=verbose)
        configs[device] = config

    parsed_vrrp_dict = parse_vrrp(configs, VRRP_REGEX)

    for device, params in parsed_inventory.items():
        generated_config = generate_config(parsed_vrrp_dict[device])
        connection = helpers.connect(address=params['address'],
                        username=params['username'],
                        password=params['password'],
                        port=params['port'])
        connection.login()
        connection.configure()
        print(device)
        print(generated_config)
        actions = helpers.run_commands(connection, generated_config, verbose=verbose)
        helpers.commit_and_save(connection, actions, verbose=True)
        connection.exit()
        connection.logout()
        
if __name__ == '__main__':
    main('inventory.yaml', verbose=True)


