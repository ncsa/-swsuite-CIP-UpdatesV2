import subprocess
import yaml


def generate_config():
    config_as_dict = get_data_for_config()
    config_as_dict = verify(config_data=config_as_dict)
    #print(config_as_dict)

    with open('config.yaml', 'w') as file:
        # TODO: yaml on local comp is 6.0, but hal-login 2 is 3.12. Due to this, sort_keys does not exist, which means YAML file won't have order
        documents = yaml.dump(config_as_dict, file, default_flow_style=False)

def get_data_for_config():
    
    node_info = subprocess.check_output(['sh','generate_config.sh'], stderr=subprocess.STDOUT)
    #node_info = b'NODELIST             S:C:T      MEMORY    GRES       \nhal[01-16]           2:20:4     256000    gpu:v100:4 \nhal-data             2:10:2     128000    (null)     \n'
    line = node_info.decode("utf-8").split('\n')[2]
    components = line.split()
    sct = components[1].split(":")
    
    nodes = 1 # assuming it's fixed
    ntasks_per_node = 16 # assuming it's fixed
    ntasks_per_node_cpu = 96 # assuming it's fixed
    sockets_per_node = int(sct[0])
    cores_per_socket = int(sct[1])
    cores_per_socket_cpu = 0 # TBD
    threads_per_core = int(sct[2])
    memory = int(components[2])
    GPUs = int(components[3].split(':')[2])
    memory_per_cpu = int(int(memory) / int(sockets_per_node)) # need to check math memory / total # of CPU

    config = {
            "NODES": nodes,
            "NTASKS_PER_NODE": ntasks_per_node,
            "NTASKS_PER_NODE_CPU": ntasks_per_node_cpu,
            "SOCKETS_PER_NODE": sockets_per_node,
            "CORES_PER_SOCKET": cores_per_socket,
            "CORES_PER_SOCKET_CPU": cores_per_socket_cpu,
            "THREADS_PER_CORE": threads_per_core,
            "GPUS": GPUs,
            "MEMORY_PER_CPU": memory_per_cpu
    }

    return config

def verify(config_data):

    is_config_correct = False

    while (is_config_correct == False):
        print_dialog(config_data)
        verify_data_response = input("Would you like to modify or add the config [Y]/[N]: ").upper()
        
        if (verify_data_response == "Y"):
            modification_response = input("Enter key:value pairs seperated by a commma that should be modified or added \n")
            list_of_modifications = modification_response.split(",")
            for item in list_of_modifications:
                item = item.strip(" ")    
                key_value = item.split(":")
                key_value[0] = key_value[0].strip(" ")
                key_value[1] = key_value[1].strip(" ")

                print("key name: " + key_value[0])
                print("value: " + key_value[1])
                print("value type: " + str(type(key_value[1])))
                print("---------------------")

                try:
                    new_value = int(key_value[1])
                except:
                    new_value = key_value[1]

                if key_value[0] not in config_data:
                    config_data[key_value[0]] = new_value
                elif (type(config_data[key_value[0]]) == type(new_value)):
                    config_data[key_value[0]] = new_value
                else:
                    print("Not valid data type for this key")

        elif verify_data_response == "N":
            break
        else:
            print("Please enter a valid response")
    
    return config_data
    
def print_dialog(config_data):
    dialog = ""
    for key, value in config_data.items():
        dialog = dialog + str(key) + " : "  + str(value) + "\n"
    print("------------------- ")
    print(dialog[:len(dialog) - 1])
    print("-------------------")
    

if __name__ == '__main__':
    generate_config()

    # Current Problems 
    # TODO: The yaml doesn't print in the correct order 
    


