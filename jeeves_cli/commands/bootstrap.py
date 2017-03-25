import os
import subprocess

import click

from jeeves_commons.constants import (DEFAULT_NUM_MINION_WORKERS,
                                      DEFAULT_NUM_OF_MINIONS)
from jeeves_cli.exceptions import CLIParameterException
from jeeves_cli.local_storage import storage
from jeeves_cli.bootstraper import JeevesBootstrapper


@click.command(name='bootstrap',
               help='Bootstrap Jeeves-CI.')
@click.option('-m', '--number-of-minions', required=False, type=int,
              help='The number of minions to start. Default is set to: {}.'
              .format(DEFAULT_NUM_OF_MINIONS),
              default=DEFAULT_NUM_OF_MINIONS)
@click.option('-w', '--number-of-workers', required=False, type=int,
              help='The number of workers per Jeeves minion'
                   ' Default is set to: {}'.format(DEFAULT_NUM_MINION_WORKERS),
              default=DEFAULT_NUM_MINION_WORKERS)
def bootstrap(number_of_minions,
              number_of_workers):
    pass


@click.command(name='bootstrap-local',
               help='Bootstrap Jeeves-CI locally.')
@click.option('-m', '--number-of-minions', required=False, type=int,
              help='The number of minions to start. Default is set to: {}.'
              .format(DEFAULT_NUM_OF_MINIONS),
              default=DEFAULT_NUM_OF_MINIONS)
@click.option('-w', '--number-of-workers', required=False, type=int,
              help='The number of workers per Jeeves minion'
                   ' Default is set to: {}'.format(DEFAULT_NUM_MINION_WORKERS),
              default=DEFAULT_NUM_MINION_WORKERS)
@click.option('-b', '--branch', required=False,
              help='The Jeeves branch to bootstrap from. Default is set '
                   'to \'master\'',
              default='master')
def bootstrap_local(number_of_minions,
                    number_of_workers,
                    branch):
    local_data = storage.get_local_data()
    if not local_data or not os.path.isdir(storage.get_project_root()):
        raise CLIParameterException('Not initialized. Run \'jvs init\'.')

    if not _docker_installed():
        raise CLIParameterException('Running Jeeves-CI locally requires '
                                    'having Docker installed.')

    if not _docker_privileged():
        raise CLIParameterException('Jeeves CLI can not run docker containers'
                                    ' in privileged mode. Please run '
                                    '\'sudo usermod -aG docker $USER\''
                                    ' and start a new bash session.')

    bs = JeevesBootstrapper()
    bs.bootstrap(num_minions=number_of_minions,
                 num_workers=number_of_workers,
                 branch=branch)

    storage.set_rabbitmq_ip(bs.rabbit_host_ip)
    storage.set_postgres_ip(bs.postgres_host_ip)
    storage.set_master_ip(bs.master_host_ip)
    print 'Jeeves local-bootstrap ended successfully.'
    print 'RESTful endpoint available at {0}:{1}'\
          .format(bs.master_host_ip, '8080')
    print 'Web-UI endpoint available at {0}:{1}'\
          .format(bs.master_host_ip, '7778')


def _docker_installed():
    result = subprocess.call('which docker', shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result == 0


def _docker_privileged():
    result = subprocess.call('docker images', shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result == 0
