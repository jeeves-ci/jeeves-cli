import subprocess

import click

from jeeves_commons.constants import (DEFAULT_NUM_MINION_WORKERS,
                                      DEFAULT_NUM_OF_MINIONS,
                                      DEFAULT_JEEVES_ADMIN_EMAIL,
                                      DEFAULT_JEEVES_ADMIN_PASSWORD)
from jeeves_rest_client.client import JeevesClient

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
              default=None)
@click.option('-u', '--username', required=False,
              help='The Jeeves-Master email address',
              default=DEFAULT_JEEVES_ADMIN_EMAIL)
@click.option('-p', '--password', required=False,
              help='The Jeeves-Master password',
              default=DEFAULT_JEEVES_ADMIN_PASSWORD)
@click.option('--verbose', '-v', is_flag=True, help='View verbose info.',
              default=False)
def bootstrap_local(number_of_minions,
                    number_of_workers,
                    branch,
                    username,
                    password,
                    verbose):
    local_data = storage.get_local_data()
    if local_data:
        raise CLIParameterException('Local env already exists. '
                                    'Run \'jvc init\' to reset.')

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
                 username=username,
                 password=password,
                 branch=branch,
                 verbose=verbose)

    storage.set_rabbitmq_ip(bs.rabbit_host_ip)
    storage.set_postgres_ip(bs.postgres_host_ip)
    storage.set_master_ip(bs.master_host_ip)

    client = JeevesClient(host=bs.master_host_ip)
    res, _ = client.login.login(username=username, password=password)
    storage.set_access_token(res.access_token)

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
