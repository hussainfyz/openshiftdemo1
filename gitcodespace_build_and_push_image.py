import os
import subprocess
import json
import platform
import logging
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load config.json
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from config.json"""
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file {CONFIG_FILE} not found!")
        exit(1)
    except json.JSONDecodeError:
        logging.error("Error parsing config.json!")
        exit(1)

def run_command(command, check_output=False):
    """Run a shell command and log output"""
    try:
        if check_output:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            logging.info(result.strip())
            return result.strip()
        else:
            subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}")
        logging.error(e.output if check_output else e)
        exit(1)

def get_os_info():
    """Determine OS name and version"""
    os_name = platform.system().lower()
    os_version = platform.version()
    logging.info(f"Detected OS: {os_name}, Version: {os_version}")
    return os_name, os_version

def check_installed(command):
    """Check if a command exists in the system"""
    return shutil.which(command) is not None

def install_docker(os_name):
    """Install Docker based on OS"""
    logging.info("Docker not found. Installing Docker...")

    if os_name == "linux":
        run_command("curl -fsSL https://get.docker.com | sh")
        run_command("sudo systemctl start docker")
        run_command("sudo systemctl enable docker")
    elif os_name == "darwin":
        logging.info("Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop")
    elif os_name == "windows":
        logging.info("Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop")
    else:
        logging.error("Unsupported OS for Docker installation!")
        exit(1)

def install_openshift_cli(os_name):
    """Install OpenShift CLI (oc) based on OS"""
    logging.info("OpenShift CLI (oc) not found. Installing...")

    if os_name == "linux":
        run_command("curl -L https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz | tar -xz")
        run_command("sudo mv oc /usr/local/bin/")
    elif os_name == "darwin":
        run_command("brew install openshift-cli")
    elif os_name == "windows":
        logging.info("Please install OpenShift CLI manually from https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/")
    else:
        logging.error("Unsupported OS for OpenShift CLI installation!")
        exit(1)

def docker_login(username, password):
    """Login to Docker Hub"""
    logging.info("Logging into Docker Hub...")
    run_command(f"echo '{password}' | docker login -u '{username}' --password-stdin")

def build_docker_image(repo):
    """Build Docker image"""
    logging.info(f"Building Docker image {repo}:latest...")
    run_command(f"docker build -t {repo}:latest .")

def push_docker_image(repo):
    """Push Docker image to Docker Hub"""
    logging.info(f"Pushing Docker image {repo}:latest to Docker Hub...")
    run_command(f"docker push {repo}:latest")

def deploy_openshift(app_name, oc_cluster, repo):
    """Deploy application on OpenShift"""
    logging.info("Logging into OpenShift...")
    run_command(f"oc login --token=sha256~_5yBb-OA6w5kfj6XYaqxFjtD8Ksslkaz4SIhrev3HUg --server=https://api.rm2.thpm.p1.openshiftapps.com:6443")

    logging.info(f"Deploying {app_name} on OpenShift from {repo}:latest...")
    run_command(f"oc new-app {repo}:latest --name={app_name} || oc rollout restart deployment/{app_name}")
    
    logging.info("Exposing service...")
    run_command(f"oc expose svc/{app_name}")

def main():
    """Main deployment process"""
    logging.info("Starting environment setup...")

    config = load_config()
    
    docker_username = config.get("docker_username")
    docker_password = config.get("docker_password")
    docker_repo = config.get("docker_repo")
    oc_cluster = config.get("oc_cluster")
    app_name = config.get("app_name", "fastapi-worker")

    if not docker_username or not docker_password or not docker_repo or not oc_cluster:
        logging.error("Missing required configuration values in config.json!")
        exit(1)

    os_name, os_version = get_os_info()

    # Check and install Docker if not found
    if not check_installed("docker"):
        install_docker(os_name)
    else:
        logging.info("Docker is already installed.")

    # Check and install OpenShift CLI if not found
    if not check_installed("oc"):
        install_openshift_cli(os_name)
    else:
        logging.info("OpenShift CLI is already installed.")

    # Verify installations
    run_command("docker --version", check_output=True)
    run_command("oc version", check_output=True)

    # Login to Docker Hub
    docker_login(docker_username, docker_password)

    # Build and push Docker image
    build_docker_image(docker_repo)
    push_docker_image(docker_repo)

    # Deploy to OpenShift
    deploy_openshift(app_name, oc_cluster, docker_repo)

    logging.info(f"Deployment complete! App {app_name} is live on OpenShift.")

if __name__ == "__main__":
    main()
