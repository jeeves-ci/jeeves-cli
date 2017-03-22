import os

# CLI local storage constants
CLI_WORKDIR = os.path.join(os.path.expanduser("~"), '.jvc')
MASTER_LOGS_PATH = '/tmp/jvc_master_logs'
MINION_LOGS_PATH = '/tmp/jvc_minion_logs'
MASTER_LOG_FILE = os.path.join(MASTER_LOGS_PATH, 'master_data.json')
CLI_LOCAL_DATA_FILE = os.path.join(CLI_WORKDIR, 'jvc_data.json')

# Execution docker images
RABBITMQ_DOCKER_IMAGE = 'rabbitmq:latest'
PYTHON_DOCKER_IMAGE = 'python:2.7'
POSTGRES_DOCKER_IMAGE = 'postgres:latest'
