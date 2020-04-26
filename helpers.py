import vymgmt
import yaml 
import logging
from tabulate import tabulate

def parse_yaml(file):   
    '''
    Just parsing yaml and returing the native python object.
    file(str): name of yaml file
    '''
    with open(file) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return(result)

def string_to_list(raw_string):
    '''
    Converting the string to list of line separated by \n
    raw_string(string)

    Return: list
    '''
    clean_list = []
    for line in raw_string.splitlines():
        clean_line = line.strip()
        clean_list.append(clean_line)
    return(clean_list)

def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter Y or N")

def filter_list(raw_list, exclude_list):
    '''
    Removing items from one list if they are in another
    raw_list(list)
    exclude_list(list)

    Return: list
    '''
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
    '''
    Provide a connection to the box
    address(string)
    username(string)
    password(string)
    port(int)

    Return: connection object
    '''
    vyos = vymgmt.Router(address, username, password=password, port=port)
    return(vyos)

def commit_and_save(connection, operation_list, commit=True, save=True, verbose=True):
    '''
    Commiting and saving the configuration based on provided arguments
    connection(connection object)
    operation_list(list): list of operations during the configuration ['show', 'set', 'delete']
    commit(bolean)
    save(bolean)
    verbose(bolean)
    '''
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

def run_show(device_params, command, verbose=True):
    '''
    Connect to the device and execute a show command
    return(list)
    '''
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
    config = connection.run_op_mode_command(command)
    logging.info('Configuration collected')
    connection.exit()
    logging.info('Exited config mode')
    connection.logout()
    logging.info('Logged out')
    listed_config = string_to_list(config)
    return(listed_config)

def run_commands(connection, commands_list, verbose=True):
    '''
    Run commands based on provided arguments
    connection(connection object)
    command_list(str)
    verbose(bolean)
    return: list of operations during the configuration ['show', 'set', 'delete']

    '''
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
    '''
    Deploy commands based on deployment plan
    device_params(dict): address, username, password=password, port=port
    commands_yaml(string): file with YAML deployment plan
    commit(bolean)
    save(bolean)
    verbose(bolean)
    '''
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
    aborted = False

    if yes_or_no('\n####: Continue with PRE deployment steps?'):
        logging.info('Starting PRE deployment activities')
        actions = run_commands(connection, plan['pre'], verbose=verbose)
        commit_and_save(connection, actions, commit=commit, save=save, verbose=True)
    else:
        logging.info('Stoping deployment')
        connection.exit()
        connection.logout()
        aborted = True

    if not aborted:
        if yes_or_no('\n####: Continue with deployment?'):
            logging.info('Starting deployment activities')
            actions = run_commands(connection, plan['commands'], verbose=verbose)
            commit_and_save(connection, actions, commit=commit, save=save, verbose=True)
        else:
            logging.info('Stoping deployment')
            connection.exit()
            connection.logout()
            aborted = True

    if not aborted:
        if yes_or_no('\n####: Continue with POST deployment steps?'):
            logging.info('Starting POST deployment activities')
            actions = run_commands(connection, plan['post'], verbose=verbose)
            commit_and_save(connection, actions, commit=commit, save=save, verbose=True)
        else:
            logging.info('Stoping deployment')
            connection.exit()
            connection.logout()
            aborted = True

    if not aborted:
        connection.exit()
        logging.info('Exited config mode')
        connection.logout()
        logging.info('Logged out')

