#Just testing the docker-py SDK
import docker

class NVDockerClient:

    def __init__(self, config):
        self.docker_client = docker.from_env(version="auto")
        self.gpu_devices = None
        if "gpu_devices" in config:
            self.gpu_devices = config["gpu_devices"]

    #TODO: Testing on MultiGPU
    def create_container(self, image, config={}):
        volumes = None
        if "volumes" in config:
            volumes = config["volumes"]
        ports = None
        if "ports" in config:
            ports = config["ports"]
        workdir = None
        if "workdir" in config:
            home_dir = config["workdir"]
        attached_devices = self.gpu_devices 
        if "attached_devices" in config:
            attached_devices = config["attached_devices"]
        auto_remove = True
        if "auto_remove" in config:
            auto_remove = config["auto_remove"]
        detach = True
        if "detach" in config:
            detach = config["detach"]
        
        c = self.docker_client.containers.run(image, "", auto_remove=auto_remove, ports=ports, devices=attached_devices, volumes=volumes, detach=detach, working_dir=workdir)
        return c.id


    def run(self, image, cmd="", config={}):
        volumes = None
        if "volumes" in config:
            volumes = config["volumes"]
        ports = None
        if "ports" in config:
            ports = config["ports"]
        workdir = None
        if "workdir" in config:
            home_dir = config["workdir"]
        attached_devices = self.gpu_devices 
        if "attached_devices" in config:
            attached_devices = config["attached_devices"]
        auto_remove = True
        if "auto_remove" in config:
            auto_remove = config["auto_remove"]
        detach = True
        if "detach" in config:
            detach = config["detach"]
        
        c = self.docker_client.containers.run(image, cmd, auto_remove=auto_remove, ports=ports, devices=attached_devices, volumes=volumes, detach=detach, working_dir=workdir)
        if cmd = "":
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
