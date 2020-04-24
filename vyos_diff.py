import click
import difflib
import helpers
import getpass

@click.command()
@click.option('--inventory', '-i', required=True)
@click.option('--exclude', '-e')
@click.option('--verbose', '-v', is_flag=True, default=True)
@click.option('--full', '-f', is_flag=True)

def main(inventory, verbose, full, exclude):
    parsed_inventory = helpers.parse_yaml(inventory)
    password = getpass.getpass('Please enter a password: ')
    
    configs = []
    for device, params in parsed_inventory.items():
        params['password'] = password
        config = helpers.show_run(params, verbose=verbose)
        configs.append(config)
    
    if exclude:
        exclude_list = helpers.parse_yaml(exclude)
        filtered_left = helpers.filter_list(configs[0], exclude_list)
        filtered_right = helpers.filter_list(configs[1], exclude_list)
        diff = difflib.ndiff(filtered_left, filtered_right)
    else:
        diff = difflib.ndiff(configs[0], configs[1])
    
    for line in diff:
        if full:
            print(line.strip())
        else:
           if line.startswith(('*', '?', '+', '-')):
                print(line.strip())

if __name__ == "__main__":
    main()
