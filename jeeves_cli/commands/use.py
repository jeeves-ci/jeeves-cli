import click

from jeeves_cli.local_storage import storage
from jeeves_cli.exceptions import CLIParameterException


@click.command(name='use', help='Point CLI to use different master IP.')
@click.option('-p', '--public-ip', required=True,
              help='The Jeeves-Master public IP.')
def use(public_ip):
    print 'Initializing Jeeves CLI\'s local env.'
    master_ip = storage.get_master_ip()
    if master_ip:
        raise CLIParameterException('A local jeeves already exists.'
                                    'Use the \'jvc init\' command.')
    storage.set_master_ip(public_ip)

    print 'Jeeves CLI now using Jeeves-Master at {0}'.format(public_ip)
