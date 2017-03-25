import logging
import os
import uuid

import jeeves_cli.docker_helper as docker
from jeeves_cli.constants import (PYTHON_DOCKER_IMAGE,
                                  RABBITMQ_DOCKER_IMAGE,
                                  POSTGRES_DOCKER_IMAGE)
from jeeves_commons.constants import (RABBITMQ_HOST_IP_ENV,
                                      POSTGRES_HOST_IP_ENV,
                                      NUM_MINION_WORKERS_ENV,
                                      DEFAULT_BROKER_PORT,
                                      DEFAULT_POSTGRES_PORT,
                                      MASTER_HOST_PORT_ENV,
                                      DEFAULT_REST_PORT)
from jeeves_commons.utils import wait_for_port, which


logger = logging.getLogger('bootstrap_logger')
logger.addHandler(logging.StreamHandler())
logger.level = logging.INFO

MASTER_CONT_NAME = 'jeeves_master_container'
MINION_CONT_NAME_PREFIX = 'jeeves_minion_container'
RABBITMQ_CONT_NAME = 'jeeves_rabbitmq_container'
POSTGRES_CONT_NAME = 'jeeves_postgres_container'

MINION_VOLUMES_LOCAL = ['/var/run/docker.sock',
                        which('docker')]


class JeevesBootstrapper(object,):
    def __init__(self,
                 rabbit_host_ip=None,
                 postgres_host_ip=None,
                 master_host_ip=None):
        self.rabbit_host_ip = rabbit_host_ip
        self.postgres_host_ip = postgres_host_ip
        self.master_host_ip = master_host_ip

    def bootstrap(self, num_minions, num_workers, branch='master'):
        self._pull_base_images()
        self._start_postgres_container()
        self._start_rabbitmq_container()

        self._start_master_container(branch=branch)

        self.start_minion_containers(num_minions,
                                     num_workers=num_workers,
                                     branch=branch)
        #  TODO: add if debug:
        # docker run --name some-pgadmin4 --link jeeves_postgres_container
        # :postgres -p 5050:5050 -d fenglc/pgadmin4

    @staticmethod
    def teardown():
        logger.info('Terminating Jeeves Minion containers..')
        docker.remove_container_by_name('{}*'.format(MINION_CONT_NAME_PREFIX))
        logger.info('Terminating Jeeves Master container..')
        docker.remove_container_by_name(MASTER_CONT_NAME)
        logger.info('Terminating Rabbitmq Broker container')
        docker.remove_container_by_name(RABBITMQ_CONT_NAME)
        logger.info('Terminating postgres DB container')
        docker.remove_container_by_name(POSTGRES_CONT_NAME)

    @staticmethod
    def kill_client_by_ip(ip):
        return docker.remove_container_by_ip(ip=ip)

    def _pull_base_images(self, verbose=False):
        logger.info('Pulling required docker images..')

        self._pull_image(PYTHON_DOCKER_IMAGE, verbose=verbose)
        self._pull_image(POSTGRES_DOCKER_IMAGE, verbose=verbose)
        self._pull_image(RABBITMQ_DOCKER_IMAGE, verbose=verbose)

    @staticmethod
    def _pull_image(full_image_name, verbose=False):
        if not docker.image_exists(full_image_name):
            logger.info('Pulling {} base image..'.format(full_image_name))
            image_name, tag = full_image_name.split(':')
            docker.pull_image(name=image_name, tag=tag, stream=verbose)

    def _start_master_container(self, branch='master'):
        # Install and start jeeves master
        cmd = ['sh', '-c', '-e',
               'git clone https://github.com/jeeves-ci/jeeves-master.git && '
               'cd jeeves-master && '
               'git checkout {branch} && '
               'pip install -r requirements.txt . && '
               'python rest_service/server.py'.format(branch=branch)]
        env = {
            RABBITMQ_HOST_IP_ENV: self.rabbit_host_ip,
            POSTGRES_HOST_IP_ENV: self.postgres_host_ip,
            MASTER_HOST_PORT_ENV: DEFAULT_REST_PORT
        }
        volumes, volume_binds = self._get_service_volumes('/tmp')
        logger.info('Starting Jeeves master container..')
        cid = docker.create_and_start_container(
                                 PYTHON_DOCKER_IMAGE,
                                 name=MASTER_CONT_NAME,
                                 command=cmd,
                                 environment=env,
                                 volumes=volumes,
                                 volume_binds=volume_binds)
        cip = docker.get_container_ip(cid)
        logger.info('Started Jeeves Master at {}'.format(cip))
        if not wait_for_port(cip, DEFAULT_REST_PORT, 120):
            docker.remove_container(cid)
            raise RuntimeError('Timed out waiting for Jeeves Master to start.')
        self.master_host_ip = cip
        return cip

    @staticmethod
    def _get_service_volumes(tmp_dir, *args):
        volumes = {}
        volume_binds = {}

        tmp_dir_volume, tmp_dir_volume_binds = docker.get_volume(tmp_dir,
                                                                 ro=False)
        volume_binds.update(tmp_dir_volume_binds)
        volumes.update(tmp_dir_volume)

        for arg in args:
            volume, binds = docker.get_volume(arg, ro=True)
            volume_binds.update(binds)
            volumes.update(volume)

        return volumes, volume_binds

    def start_minion_containers(self,
                                num_minions=None,
                                num_workers='',
                                branch='master'):
        logger.info('Starting {} Jeeves minion containers..'
                    .format(num_minions))
        # Install the minion on each of the containers
        cmd = ['sh', '-c', '-e',
               'git clone https://github.com/jeeves-ci/jeeves-minion.git && '
               'cd jeeves-minion && '
               'git checkout {branch} && '
               'pip install -r requirements.txt . && '
               'python jeeves_minion/minion.py'.format(branch=branch)]

        volumes, volume_binds = self._get_service_volumes(
                                                        '/tmp',
                                                        *MINION_VOLUMES_LOCAL)
        env = {
            RABBITMQ_HOST_IP_ENV: self.rabbit_host_ip,
            POSTGRES_HOST_IP_ENV: self.postgres_host_ip,
            NUM_MINION_WORKERS_ENV: num_workers
        }

        for i in xrange(num_minions):
            cid = docker.create_and_start_container(
                                   PYTHON_DOCKER_IMAGE,
                                   name='{0}_{1}'
                                        .format(MINION_CONT_NAME_PREFIX,
                                                str(uuid.uuid4())),
                                   volumes=volumes,
                                   environment=env,
                                   volume_binds=volume_binds,
                                   command=cmd)
            logger.info('Started new minion at {}'
                        .format(docker.get_container_ip(cid)))

    def _start_rabbitmq_container(self):
        logger.info('Starting Rabbitmq service container..')
        container_id = docker.create_and_start_container(
            image=RABBITMQ_DOCKER_IMAGE,
            name=RABBITMQ_CONT_NAME)

        self.rabbit_host_ip = docker.get_container_ip(container_id)
        logger.info('waiting for rabbitmq service port on {host}:{port}'
                    .format(host=self.rabbit_host_ip,
                            port=DEFAULT_BROKER_PORT))
        if not wait_for_port(self.rabbit_host_ip, DEFAULT_BROKER_PORT):
            docker.remove_container(container_id)
            raise RuntimeError('Timed out waiting for rabbitmq service.')

    def _start_postgres_container(self):
        logger.info('Starting Postgres service container..')
        container_id = docker.create_and_start_container(
            image=POSTGRES_DOCKER_IMAGE,
            name=POSTGRES_CONT_NAME)

        self.postgres_host_ip = docker.get_container_ip(container_id)
        logger.info('waiting for postgres service port on {host}:{port}'
                    .format(host=self.postgres_host_ip,
                            port=DEFAULT_POSTGRES_PORT))
        if not wait_for_port(self.postgres_host_ip, DEFAULT_POSTGRES_PORT):
            docker.remove_container(container_id)
            raise RuntimeError('Timed out waiting for postgres service.')

    @staticmethod
    def _get_project_root(project_name):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        setup_py_path = os.path.join(curr_path, '..', '..',
                                     project_name, 'setup.py')
        if not os.path.exists(setup_py_path):
            raise RuntimeError('Project root not found or does not contain a '
                               'setup.py file: {0}'.format(setup_py_path))
        return os.path.abspath(os.path.dirname(setup_py_path))


if __name__ == '__main__':
    app = JeevesBootstrapper()
    app.bootstrap(1, 3)
    # app.stop()
