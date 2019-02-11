
import os 
from subprocess import check_output
import re
import docker
from py3nvml.py3nvml import *

class NVDockerClient:

    nvml_initialized = False

    def __init__(self):
        self.docker_client = docker.from_env(version="auto")
        NVDockerClient.__check_nvml_init()

    """
    Private method to check if nvml is loaded (and load the library if it isn't loaded)
    """
    def __check_nvml_init():
        if not NVDockerClient.nvml_initialized:
            nvmlInit()
            print("NVIDIA Driver Version:", nvmlSystemGetDriverVersion())
            NVDockerClient.nvml_initialized = True

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
        NVDockerClient.__check_nvml_init()
        gpus = {}
        num_gpus = nvmlDeviceGetCount()
        for i in range(num_gpus):
            gpu_handle = nvmlDeviceGetHandleByIndex(i)
            gpu_name = nvmlDeviceGetName(gpu_handle)
            gpus[i] = {"gpu_handle": gpu_handle, "gpu_name": gpu_name}
        return gpus

    @staticmethod
    def gpu_memory_usage(id):
        gpus = NVDockerClient.gpu_info()
        if id not in gpus.keys():
            return None
        gpu_handle = gpus[id]["gpu_handle"]
        gpu_memory_data = nvmlDeviceGetMemoryInfo(gpu_handle)
        rv = {}
        #returns in megabytes
        rv["used_mb"] = gpu_memory_data.used/1e6
        rv["free_mb"] = gpu_memory_data.free/1e6
        return rv

    @staticmethod
    def least_used_gpu():
        gpus = NVDockerClient.gpu_info()
        lowest_key = None;
        lowest_used_memory = 1e9;
        for id in gpus.keys():
            memory = NVDockerClient.gpu_memory_usage(id)["used_mb"]
            if lowest_key is None or memory < lowest_used_memory:
                lowest_key = id
                lowest_used_memory = memory
        return lowest_key
