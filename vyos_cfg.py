import helpers
import getpass 
import click

@click.command()
@click.option('--inventory', '-i', required=True, help='Inventory YAML')
@click.option('--commands', '-c', required=True, help='Command list (YAML)')
@click.option('--save', '-s', is_flag=True, default=True, help='Whether to save config or not')
@click.option('--verbose', '-v', is_flag=True, default=True, help='Verbose mode (by default)')
def main(inventory, commands, save, verbose):
    parsed_inventory = helpers.parse_yaml(inventory)
    password = getpass.getpass('Please enter a password: ')
    for device, params in parsed_inventory.items():
        params['password'] = password
        helpers.deploy(params, commands, save=save, verbose=verbose)

if __name__ == "__main__":
    main()
