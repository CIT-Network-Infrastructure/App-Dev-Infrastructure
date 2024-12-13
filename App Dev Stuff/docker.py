import docker
import argparse

class DockerContainerManager:
    def __init__(self):
        self.client = docker.from_env()

    def create_container(self, image, name=None, ports=None, volumes=None, environment=None):
        """
        Create a new Docker container
        
        :param image: Docker image to use
        :param name: Optional name for the container
        :param ports: Optional port mappings (dict)
        :param volumes: Optional volume mappings (dict)
        :param environment: Optional environment variables (dict)
        :return: Created container object
        """
        try:
            container = self.client.containers.create(
                image=image,
                name=name,
                ports=ports or {},
                volumes=volumes or {},
                environment=environment or {},
                detach=True
            )
            print(f"Container created: {container.id}")
            return container
        except Exception as e:
            print(f"Error creating container: {e}")
            return None

    def start_container(self, container_id_or_name):
        """
        Start a specific container
        
        :param container_id_or_name: Container ID or name
        """
        try:
            container = self.client.containers.get(container_id_or_name)
            container.start()
            print(f"Container started: {container.id}")
        except Exception as e:
            print(f"Error starting container: {e}")

    def stop_container(self, container_id_or_name):
        """
        Stop a specific container
        
        :param container_id_or_name: Container ID or name
        """
        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            print(f"Container stopped: {container.id}")
        except Exception as e:
            print(f"Error stopping container: {e}")

    def remove_container(self, container_id_or_name, force=False):
        """
        Remove a specific container
        
        :param container_id_or_name: Container ID or name
        :param force: Force remove running container
        """
        try:
            container = self.client.containers.get(container_id_or_name)
            container.remove(force=force)
            print(f"Container removed: {container.id}")
        except Exception as e:
            print(f"Error removing container: {e}")

    def list_containers(self, all=False):
        """
        List containers
        
        :param all: Include stopped containers
        :return: List of containers
        """
        try:
            containers = self.client.containers.list(all=all)
            for container in containers:
                print(f"ID: {container.id}, Name: {container.name}, Status: {container.status}")
            return containers
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description="Docker Container Management")
    parser.add_argument('action', choices=['create', 'start', 'stop', 'remove', 'list'],
                        help='Action to perform on containers')
    parser.add_argument('--image', help='Docker image for container creation')
    parser.add_argument('--name', help='Container name')
    parser.add_argument('--ports', nargs='+', help='Port mappings (format: host:container)')
    
    args = parser.parse_args()
    
    manager = DockerContainerManager()
    
    if args.action == 'create':
        if not args.image:
            print("Image is required for container creation")
            return
        
        # Parse ports if provided
        ports = {}
        if args.ports:
            for port_map in args.ports:
                host, container = port_map.split(':')
                ports[container] = host
        
        manager.create_container(
            image=args.image, 
            name=args.name, 
            ports=ports
        )
    
    elif args.action == 'start':
        if not args.name:
            print("Container name or ID is required")
            return
        manager.start_container(args.name)
    
    elif args.action == 'stop':
        if not args.name:
            print("Container name or ID is required")
            return
        manager.stop_container(args.name)
    
    elif args.action == 'remove':
        if not args.name:
            print("Container name or ID is required")
            return
        manager.remove_container(args.name)
    
    elif args.action == 'list':
        manager.list_containers(all=True)

if __name__ == "__main__":
    main()