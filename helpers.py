import vymgmt
import yaml 
import logging
from tabulate import tabulate

def parse_yaml(file):
    with open(file) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return(result)

def get_commands_list(file):
    with open(file) as file:
        commands = file.read().split('\n')
    return commands[0:-1]

def string_to_list(raw_string):
    clean_list = []
    for line in raw_string.splitlines():
        clean_line = line.strip()
        clean_list.append(clean_line)
    return(clean_list)

def filter_list(raw_list, exclude_list):
    filtered_list = []
    for item in raw_list:
        for keyword in exclude_list:
            if keyword in item:
                break
        else:
            filtered_list.append(item)
    unique_list = []
    for item in filtered_list:
        if item not in unique_list:
            unique_list.append(item)
    return(unique_list)

def connect(address, username, password, port):
    vyos = vymgmt.Router(address, username, password=password, port=port)
    return(vyos)

def commit_and_save(connection, operation_list, commit=True, save=True, verbose=True):
    if verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",level=logging.DEBUG)
    if operation_list == {'show'}:
        logging.info('No need to commit(show commands only)')
        commit = False
        save = False
    else:
        if commit:
            logging.info('Trying to commit')
            try:
                connection.commit()
                logging.info('Commited')
            except vymgmt.router.ConfigError:
                logging.warning('No configuration changes to commit')
        if save:
            logging.info('Trying to save')
            connection.save()
            logging.info('Saved')

def show_run(device_params, verbose=True):
    if verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",level=logging.DEBUG)
    connection = connect(address=device_params['address'],
                        username=device_params['username'],
                        password=device_params['password'],
                        port=device_params['port'])
    connection.login()
    logging.info('Logged in into the "{}"'.format(device_params['address']))
    connection.configure()
    logging.info('Entered into config mode')
    config = connection.run_op_mode_command('show configuration commands | no-more')
    logging.info('Configuration collected')
    connection.exit()
    logging.info('Exited config mode')
    connection.logout()
    logging.info('Logged out')
    listed_config = string_to_list(config)
    return(listed_config)

def run_commands(connection, commands_list, verbose=True):
    if verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",level=logging.DEBUG)
    operation_list = set()
    for command in commands_list:
        operator = command.split()[0]
        branch = ' '.join(command.split()[1::])
        if operator == 'set':
            operation_list.add(operator)
            logging.info('Trying to set "{}"'.format(branch))
            try:
                connection.set(branch)
                logging.info('Succesfuly set')
            except vymgmt.router.ConfigError:
                logging.warning('Configuration path already exists')
        elif operator == 'delete':
            logging.info('Trying to delete "{}"'.format(branch))
            operation_list.add(operator)
            try:
                connection.delete(branch)
                logging.info('Succesfuly deleted')
            except vymgmt.router.ConfigError:
                logging.warning('Nothing to delete')
        elif operator == 'show':
            logging.info('Trying to execute "{}"'.format(command))
            operation_list.add(operator)
            output = connection.run_op_mode_command(command)
            print(tabulate([[output]], tablefmt='grid'))
        else:
            raise('Command is not supported')
    return(operation_list)

def deploy(device_params, commands_yaml, commit=True, save=True, verbose=True):
    if verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",level=logging.DEBUG)

    plan = parse_yaml(commands_yaml)
    print('\n' + '#'*100)
    print('Starting for {}'.format(device_params['address']))
    print('#' * 100)

    logging.info('Deployment plan in {} parsed'.format(commands_yaml))

    connection = connect(address=device_params['address'],
                        username=device_params['username'],
                        password=device_params['password'],
                        port=device_params['port'])
    connection.login()
    logging.info('Logged in into the "{}"'.format(device_params['address']))
    connection.configure()
    logging.info('Entered into config mode')

    logging.info('Starting PRE deployment activities')
    actions = run_commands(connection, plan['pre'], verbose=verbose)
    commit_and_save(connection, actions, commit=commit, save=save, verbose=True)

    logging.info('Starting deployment activities')
    actions = run_commands(connection, plan['commands'], verbose=verbose)
    commit_and_save(connection, actions, commit=commit, save=save, verbose=True)

    logging.info('Starting POST deployment activities')
    actions = run_commands(connection, plan['post'], verbose=verbose)
    commit_and_save(connection, actions, commit=commit, save=save, verbose=True)

    connection.exit()
    logging.info('Exited config mode')
    connection.logout()
    logging.info('Logged out')
