import helpers
import getpass 
import click

@click.command()
@click.option('--inventory', '-i', required=True)
@click.option('--commands', '-c', required=True)
@click.option('--save', '-s', is_flag=True, default=True)
@click.option('--verbose', '-v', is_flag=True, default=True)
def main(inventory, commands, save, verbose):
    parsed_inventory = helpers.parse_yaml(inventory)
    password = getpass.getpass('Please enter a password: ')
    for device, params in parsed_inventory.items():
        params['password'] = password
        helpers.deploy(params, commands, save=save, verbose=verbose)

if __name__ == "__main__":
    main()
