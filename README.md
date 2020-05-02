**vyos_cfg.py:** A simple script for managing two instances of VyOS. It can send a predifined list of commands to devices. It aslo supports PRE and POST steps.

**vyos_diff.py:** A simple script for getting a diff between device configuration.

# vyos_cfg.py
A simple script for managing two instances of VyOS. It can send a predifined list of commands to devices. It aslo supports PRE and POST steps.

## Files
```
.
├── commands.yaml         List of commands to be executed (with pre- and post- steps)
├── helpers.py            Main functions
├── inventory.yaml        Inventory file
└── vyos_cfg.py           Script for configuring device
```

#### inventory.yaml
Contains basic connectivity details for every host
```
# cat inventory.yaml
novac:
    address: 10.20.30.2
    username: melhiour
    port: 1280
thiem:
    address: 10.20.30.3
    username: melhiour
    port: 1280
```

#### commands.yaml
Here we have commands for every "step": PRE deployment, deployment and POST deployments. After every step configuration will be commited. Before execution user will be asked Yes/No question. So, it can be used in relativelly complex deployments (see execution example for details). Note, all commands will be executed for both devices in sequential manner.
```
# cat commands.yaml
pre:
    - show configuration commands | match 'firewall name L2TP-TO-PROD rule 100'
commands:
    - set firewall name L2TP-TO-PROD rule 100 destination port '22'
post:
    - show configuration commands | match 'firewall name L2TP-TO-PROD rule 100'
```

#### Execution example
```
# python vyos_cfg.py --help
Usage: vyos_cfg.py [OPTIONS]

Options:
  -i, --inventory TEXT  Inventory YAML  [required]
  -c, --commands TEXT   Command list (YAML)  [required]
  -s, --save            Whether to save config or not
  -v, --verbose         Verbose mode (by default)
  --help                Show this message and exit.
  
# python vyos_cfg.py -i inventory.yaml -c commands.yaml
Please enter a password:

####################################################################################################
Starting for 10.20.30.2
####################################################################################################
INFO: Deployment plan in commands.yaml parsed
INFO: Logged in into the "10.20.30.2"
INFO: Entered into config mode

####: Continue with PRE deployment steps? (y/n): y
INFO: Starting PRE deployment activities
INFO: Trying to execute "show configuration commands | match 'firewall name L2TP-TO-PROD rule 100'"
+---------------------------------------------------------------------------+
| run show configuration commands | match 'firewall name L2TP-TO-P          |
| ROD rule 100'                                                             |
| set firewall name L2TP-TO-PROD rule 100 action 'accept'                   |
| set firewall name L2TP-TO-PROD rule 100 description 'Access to Arcadia'   |
| set firewall name L2TP-TO-PROD rule 100 destination address '10.20.30.11' |
| set firewall name L2TP-TO-PROD rule 100 destination port '22'             |
| set firewall name L2TP-TO-PROD rule 100 protocol 'tcp'                    |
| [edit]                                                                    |
|                                                                           |
| melhiour@novac                                                            |
+---------------------------------------------------------------------------+
INFO: No need to commit(show commands only)

####: Continue with deployment? (y/n): y
INFO: Starting deployment activities
INFO: Trying to set "firewall name L2TP-TO-PROD rule 100 destination port '22'"
WARNING: Configuration path already exists
INFO: Trying to commit
WARNING: No configuration changes to commit
INFO: Trying to save
INFO: Saved

####: Continue with POST deployment steps? (y/n): y
INFO: Starting POST deployment activities
INFO: Trying to execute "show configuration commands | match 'firewall name L2TP-TO-PROD rule 100'"
+---------------------------------------------------------------------------+
| run show configuration commands | match 'firewall name L2TP-TO-P          |
| ROD rule 100'                                                             |
| set firewall name L2TP-TO-PROD rule 100 action 'accept'                   |
| set firewall name L2TP-TO-PROD rule 100 description 'Access to Arcadia'   |
| set firewall name L2TP-TO-PROD rule 100 destination address '10.20.30.11' |
| set firewall name L2TP-TO-PROD rule 100 destination port '22'             |
| set firewall name L2TP-TO-PROD rule 100 protocol 'tcp'                    |
| [edit]                                                                    |
|                                                                           |
| melhiour@novac                                                            |
+---------------------------------------------------------------------------+
INFO: No need to commit(show commands only)
INFO: Exited config mode
INFO: Logged out

####################################################################################################
Starting for 10.20.30.3
####################################################################################################
INFO: Deployment plan in commands.yaml parsed
INFO: Logged in into the "10.20.30.3"
INFO: Entered into config mode

####: Continue with PRE deployment steps? (y/n): n
INFO: Stoping deployment
```

# vyos_diff.py
Just a simple script for getting a diff between device configuration.

## Files
```
.
├── exclude_list.yaml     List of commands to be excluded from the diff
├── helpers.py            Main functions
├── inventory.yaml        Inventory file
└── vyos_diff.py          Script for generating diff for configuration
```
#### inventory.yaml
Contains basic connectivity details for every host
```
# cat inventory.yaml
novac:
    address: 10.20.30.2
    username: melhiour
    port: 1280
thiem:
    address: 10.20.30.3
    username: melhiour
    port: 1280
```
#### exclude_list.yaml
List of lines to be excluded from the diff. For example, you can specify configuration paths which are different for sure and you don't know to see it in diff.
```
# cat exclude_list.yaml
- set system host-name
- set high-availability vrrp group
```
#### Execution example
```
# python vyos_diff.py --help
Usage: vyos_diff.py [OPTIONS]

Options:
  -i, --inventory TEXT  Inventory YAML  [required]
  -e, --exclude TEXT    YAML file with lines to be excluded from diff
  -v, --verbose         Verbose mode (by default)
  -f, --full            Display full diff insted of changes only
  --help                Show this message and exit.

# python vyos_diff.py -i inventory.yaml -e exclude_list.yaml
Please enter a password:
INFO: Logged in into the "10.20.30.2"
INFO: Entered into config mode
INFO: Configuration collected
INFO: Exited config mode
INFO: Logged out
INFO: Logged in into the "10.20.30.3"
INFO: Entered into config mode
INFO: Configuration collected
INFO: Exited config mode
INFO: Logged out
- set firewall name MONOLITH-TO-NOVAC rule 300 destination address '10.10.11.1'
?                                                                            ^
+ set firewall name MONOLITH-TO-NOVAC rule 300 destination address '10.10.11.2'
?                                                                            ^
...
```
