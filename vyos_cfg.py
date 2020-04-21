import helpers
import getpass 

INVENTORY='inventory.yaml'
COMMANDS='commands.yaml'

inventory = helpers.parse_yaml(INVENTORY)
password = getpass.getpass('Please enter a password: ')

for device, params in inventory.items():
    params['password'] = password
    helpers.deploy(params, COMMANDS, commit=True, save=True, verbose=True)
