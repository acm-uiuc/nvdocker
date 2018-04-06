
import os 
from subprocess import check_output
import re
import docker

class NVDockerClient:

    def __init__(self):
        self.docker_client = docker.from_env(version="auto")

    #TODO: Testing on MultiGPU
    def create_container(self, image, **kwargs):
        #defaults
        config = {
            "auto_remove":False,
            "detach":True
        }
        environment = {}
        for arg in kwargs:
            if arg == "driver_capabilities":
                environment["NVIDIA_DRIVER_CAPABILITIES"] = kwargs["driver_capabilities"]
            elif arg == "visible_devices" in kwargs:
                vis_devices = ""
                if type(kwargs["visible_devices"]) is list:
                    if len(kwargs["visible_devices"]) == 1:
                        vis_devices = str(kwargs["visible_devices"][0])
                    else:
                        for dev in kwargs["visible_devices"]:
                            vis_devices += dev + ','
                        vis_devices = vis_devices[:-1]
                elif type(kwargs["visible_devices"]) is str:
                    vis_devices = kwargs["visible_device"]
                elif type(kwargs["visible_devices"]) is int:
                    vis_devices = str(kwargs["visible_devices"])
                environment["NVIDIA_VISIBLE_DEVICES"] = vis_devices
            elif arg == "disable_require" in kwargs:
                environment["NVIDIA_DISABLE_REQUIRE"] = kwargs["disable_require"]
            elif arg == "require":
                if "cuda" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_CUDA"] = kwargs["require"]["cuda"]
                if "driver" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_DRIVER"] = kwargs["require"]["driver"]
                if "arch" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_ARCH"] = kwargs["require"]["arch"]
            elif arg == "cuda_version":
                print("WARNING: the CUDA_VERSION enviorment variable is a legacy variable, consider moving to NVIDIA_REQUIRE_CUDA")
                environment["CUDA_VERSION"] = kwargs["cuda_version"]
            elif arg == "environment":
                if type(kwargs["environment"]) is dict:
                    for k,v in kwargs["environment"]:
                        environment[k] = v
                elif type(kwargs["environment"]) is list:
                    for e in kwargs["environment"]:
                        kv = e.split("=")
                        assert(len(kv) == 2), "Does not follow the format SOMEVAR=xxx"
                        environment[kv[0]] = kv[1]
            else:
                config[arg] = kwargs[arg]
        config["environment"] = environment
        config["runtime"] = "nvidia"
        
        c = self.docker_client.containers.run(image, "", **config)

        return c


    def run(self, image, cmd="", **kwargs):
        #defaults
        config = {}
        environment = {}
        for arg in kwargs:
            if arg == "driver_capabilities":
                environment["NVIDIA_DRIVER_CAPABILITIES"] = kwargs["driver_capabilities"]
            elif arg == "visible_devices" in kwargs:
                vis_devices = ""
                if type(kwargs["visible_devices"]) is list:
                    if len(kwargs["visible_devices"]) == 1:
                        vis_devices = str(kwargs["visible_devices"][0])
                    else:
                        for dev in kwargs["visible_devices"]:
                            vis_devices += dev + ','
                        vis_devices = vis_devices[:-1]
                elif type(kwargs["visible_devices"]) is str:
                    vis_devices = kwargs["visible_device"]
                elif type(kwargs["visible_devices"]) is int:
                    vis_devices = str(kwargs["visible_devices"])
                environment["NVIDIA_VISIBLE_DEVICES"] = vis_devices
            elif arg == "disable_require" in kwargs:
                environment["NVIDIA_DISABLE_REQUIRE"] = kwargs["disable_require"]
            elif arg == "require":
                if "cuda" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_CUDA"] = kwargs["require"]["cuda"]
                if "driver" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_DRIVER"] = kwargs["require"]["driver"]
                if "arch" in kwargs["require"]:
                    environment["NVIDIA_REQUIRE_ARCH"] = kwargs["require"]["arch"]
            elif arg == "cuda_version":
                print("WARNING: the CUDA_VERSION enviorment variable is a legacy variable, consider moving to NVIDIA_REQUIRE_CUDA")
                environment["CUDA_VERSION"] = kwargs["cuda_version"]
            elif arg == "environment":
                if type(kwargs["environment"]) is dict:
                    for k,v in kwargs["environment"]:
                        environment[k] = v
                elif type(kwargs["environment"]) is list:
                    for e in kwargs["environment"]:
                        kv = e.split("=")
                        assert(len(kv) == 2), "Does not follow the format SOMEVAR=xxx"
                        environment[kv[0]] = kv[1]
            else:
                config[arg] = kwargs[arg]
        config["environment"] = environment
        config["runtime"] = "nvidia"

        c = self.docker_client.containers.run(image, cmd, **config)

        if cmd == "":
            return c.id
        else:
            return c

    def build_image(self, path):
        img = self.docker_client.images.build(path);
        return img
        
    def get_container_logs(self, cid):
        c = self.docker_client.containers.get(cid)
        return c.logs()

    def get_all_container_ids(self):
        return self.docker_client.containers.list()
    
    def stop_container(self, cid):
        c = self.docker_client.containers.get(cid)
        c.stop()

    def start_container(self, cid):
        c = self.docker_client.containers.get(cid)
        c.start()
    
    def start_all_containers(self):
        for c in self.docker_client.containers.list():
            c.start()
        
    def stop_all_containers(self):    
        for c in self.docker_client.containers.list():
            c.stop()

    def exec_run(self, cid, cmd):
        c = self.docker_client.containers.get(cid)
        return c.exec_run(cmd)

    @staticmethod
    def gpu_info():
        #output = check_output(["nvidia-smi", "-L"]).decode("utf-8")
        keys = ['memory_free', 'memory_used', 'memory_total']
        query_gpu = check_output(["nvidia-smi", "--query-gpu=memory.free,memory.used,memory.total","--format=csv,noheader"]).decode("utf-8")
        #regex = re.compile(r"GPU (?P<id>\d+):")
        query_gpu = query_gpu.strip()
        gpus = {}
        id = 0
        for gpu in query_gpu.split("\n"):
            gpu_info = {}
            key_id = 0
            for info in gpu.split(","):
                info = info.strip()
                gpu_info[keys[key_id]] = info.split(" ")[0];
                key_id += 1
            gpus[id] = gpu_info;
            id += 1
        return gpus

    @staticmethod
    def gpu_memory_usage(id):
        gpus = NVDockerClient.get_gpus()
        if id not in gpus.keys():
            return None
        return gpus[id]

    @staticmethod
    def least_used_gpu():
        gpus = NVDockerClient.get_gpus()
        lowest_key = None;
        for key in gpus.keys():
            if lowest_key == None and gpus[key]['memory_free'] > 0:
                lowest_key = key
            elif gpus[key]['memory_free'] < gpus[lowest_keys]['memory_free']:
                lowest_key = key
            else:
                pass

        return lowest_key
