import subprocess
from collections import OrderedDict

def generate_config():
    """
    Generates a configurations file for a chosen node based on the sinfo command.
    Writes to the configuration yaml file
    """
    
    config_as_dict = get_data_for_config()

    if (config_as_dict == None):
        return

    config_as_dict = verify(config_data=config_as_dict)
    #print(config_as_dict)
    counter = 1

    with open('../conf/config.yaml', 'w') as file:

        with open('../conf/license_for_config.txt', 'r') as license_file: 
            for line in license_file:
                file.write(line)
        file.write('#################################### Defaults and Limits ###########################################')
        file.write('---')
        file.write('\n')
        for key, value in config_as_dict.items():

            file.write(key + ': ')
            file.write(str(value))
            file.write('\n')

            if counter == 31:
                file.write('################################# Some Environment Variables #######################################\n')
            elif counter == 34:
                file.write('###################################### Other Parameters ############################################\n')
            elif counter == 37:
                file.write('################################### Error and Warning Codes ########################################')

            counter = counter + 1
        
        file.write('...')

def get_data_for_config():
    """
    Retrieves, parses, and fills in the data needed for the configuration file
    """
    
    #node_info = subprocess.check_output(['sh','generate_config.sh'], stderr=subprocess.STDOUT)
    node_info = b'NODELIST             S:C:T      MEMORY    GRES       \nhal[01-16]           2:20:4     256000    gpu:v100:4 \nhal-data             2:10:2     128000    (null)     \n'
    available_nodes = node_info.decode("utf-8").split('\n')

    print(node_info.decode("utf-8"))
    print("Note: If running on Python 2, please add double quotations to any input")
    node_selection = input("Enter the node you would like to configure with with: ")
    is_node_selection_valid = False
    i = 0
    for node in available_nodes:
        if (node == ""):
            break
        
        components = node.split()
        
        if components[0] == node_selection.strip(" ") and node_selection in node:
            node_selection = available_nodes[i]
            is_node_selection_valid = True
            break
        else:
            i = i + 1


    if is_node_selection_valid == True:
    
        if is_input_null(components[1]):
            sct = [0, 0, 0]
        else:
            sct = components[1].split(":")
            sockets_per_node = int(sct[0])
            cores_per_socket = int(sct[1])
            threads_per_core = int(sct[2])

        if is_input_null(components[2]):
            memory = 0
        else:
            memory = int(components[2])

        if is_input_null(components[3]):
            GPUs = 0
        else:
            GPUs = int(components[3].split(':')[2])

        nodes = 1 # assuming it's fixed
        ntasks_per_node = 16 # assuming it's fixed
        ntasks_per_node_cpu = 96 # assuming it's fixed

        cores_per_socket_cpu = 0 # TBD

        memory_per_cpu = int(int(memory) / int(sockets_per_node)) # need to check math memory / total # of CPU

        config = OrderedDict()
        config['PARTITION_DEFAULT'] = '\""gpux1"\"'
        config['NODES'] = nodes
        config['NTASKS_PER_NODE'] = ntasks_per_node
        config['NTASKS_PER_NODE_CPU'] = ntasks_per_node_cpu
        config['SOCKETS_PER_NODE'] = sockets_per_node
        config['CORES_PER_SOCKET'] = cores_per_socket
        config['CORES_PER_SOCKET_CPU'] = cores_per_socket_cpu
        config['THREADS_PER_CORE'] = threads_per_core
        config['GPUS'] = GPUs
        config['MEMORY_PER_CPU'] = memory_per_cpu

        config['HOURS_UL'] = 24
        config['HOURS_DEBUG'] = 4
        config['HOURS_DEFAULT'] = 4
        config['HOURS'] = 24

        config['TIME'] = "24:00:00"
        
        config['MULTIPLIER'] = 1

        config['CPU_PER_GPU_LL'] = 16
        config['CPU_PER_GPU_UL'] = 40
        config['CPU_PER_GPU'] = 16
        config['CPU_PER_GPU_DEFAULT'] = 16

        config['SLURM_RUN'] = '\"srun\"'
        config['SLURM_BATCH'] = '\"#SBATCH\"'
        config['SLURM_ALLOC'] = '\"salloc\"'
        config['SHELL'] = '\"/bin/bash\"'

        config['SHEBANG'] = '\"#!/bin/bash\"'
        config['COMMENT'] = 2
        config['BATCH_COMMAND'] = 1
        config['NON_BATCH_COMMAND'] = 0

        config['INTERACTIVE_MODE'] = 0
        config['SCRIPT_MODE'] = 1
        config['ALLOCATION_MODE'] = 2


        config['HAL_CONTAINER_REGISTRY'] = '$HAL_CONTAINER_REGISTRY' # not listed as string in orig
        config['CONTAINER_SEARCH_DEPTH_LIMIT'] = 0
        config['ALLOWED_CONTAINER_IMAGE_EXTENSIONS'] = '[".sif"]'

        config['ALLOWED_PARTITIONS'] = ["gpux1", "gpux2", "gpux3", "gpux4", "gpux8", "gpux12", "gpux16", "cpu_mini", "cpun1", "cpun2", "cpun3", "cpun4", "cpun8", "cpun12", "cpun16"]
        config['DEBUG_PARTITION'] = '\"debug\"'
        config['ALLOW_CPU_SSD'] = True

        config['VALUE_ERROR'] = -1
        config['TYPE_ERROR'] = -2
        config['WARNING'] = -3

        return config
    else:
        print("Node doesn't exist")

def verify(config_data):
    """
    Verify with user whether the information collected is correct or not 

    Parameters
    ----------
    config_data : ordered dictionary 
        An ordered dictionary contaning key:value pairs of configuration settings
    """

    is_config_correct = False

    while (is_config_correct == False):
        print_dialog(config_data)
        verify_data_response = input("Would you like to modify or add the config [Y]/[N]: ").upper()
        valid_changes_made = False
        if (verify_data_response == "Y"):
            modification_response = input("Enter [key]:[value] pairs seperated by a commma that should be modified or added (case sensitive) \n")
            list_of_modifications = modification_response.split(",")
            for item in list_of_modifications:
                item = item.strip(" ")    
                key_value = item.split(":")
                if (len(key_value) != 2):
                    print("Input of \'" + item + "\' is invalid")
                    continue
                key_value[0] = key_value[0].strip(" ")
                key_value[1] = key_value[1].strip(" ")

                try:
                    new_value = int(key_value[1])
                except:
                    new_value = key_value[1]

                valid_changes_made = True
                if key_value[0] not in config_data:
                    config_data[key_value[0]] = new_value
                elif (type(config_data[key_value[0]]) == type(new_value)):
                    config_data[key_value[0]] = new_value
                else:
                    print("Not valid data type for this key")
            
            if (valid_changes_made):
                print("Changes have been made")

        elif verify_data_response == "N":
            break
        else:
            print("Please enter a valid response")
    
    return config_data

def is_input_null(input):
    if (input == '(null)'):
        return True
    return False

def print_dialog(config_data):
    """
    Prints the configurations to console 

    Parameters
    ----------
    config_data : ordered dictionary 
        An ordered dictionary contaning key:value pairs of configuration settings
    """

    dialog = ""
    for key, value in config_data.items():
        dialog = dialog + str(key) + " : "  + str(value) + "\n"
    print("----------------------------- ")
    print(dialog[:len(dialog) - 1])
    print("-----------------------------")
    
if __name__ == '__main__':
    generate_config()
 