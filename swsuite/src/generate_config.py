import subprocess
import yaml

def get_info():
    print(yaml.__version__)
    node_info = subprocess.check_output(['sh','generate_config.sh'], stderr=subprocess.STDOUT)
    print(node_info)
    line = node_info.decode("utf-8").split('\n')[1]
    components = line.split()
    sct = components[1].split(":")
    print(components)
    print(sct)

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
    print(config)
    with open('config.yaml', 'w') as file:
        documents = yaml.dump(config, file,default_flow_style=False)


get_info()
