import click
import difflib
import helpers
import getpass

@click.command()
@click.option('--inventory', '-i', required=True)
@click.option('--verbose', '-v', is_flag=True, default=True)
@click.option('--diff-only', '-d', is_flag=True, default=True)

def main(inventory, verbose, diff_only):
    parsed_inventory = helpers.parse_yaml(inventory)
    password = getpass.getpass('Please enter a password: ')
    
    configs = []
    for device, params in parsed_inventory.items():
        params['password'] = password
        config = helpers.show_run(params, verbose=verbose)
        configs.append(config)

    diff = difflib.ndiff(configs[0].splitlines(1), configs[1].splitlines(1))
    
    for line in diff:
        print(line.strip())

if __name__ == "__main__":
    main()
