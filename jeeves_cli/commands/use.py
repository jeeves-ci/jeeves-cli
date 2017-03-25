import click

from jeeves_cli.local_storage import storage
from jeeves_cli.exceptions import CLIParameterException


@click.command(name='use', help='Point CLI to use different master IP.')
@click.option('-p', '--public-ip', required=True,
              help='The Jeeves-Master public IP.')
def use(public_ip):
    print 'Initializing Jeeves CLI\'s local env.'
    local_data = storage.get_local_data()
    if not local_data:
        raise CLIParameterException('A local jeeves env does\'nt exist.'
                                    'Use the \'jvc init\' command.')
    storage.set_master_ip(public_ip)

    print 'Jeeves CLI now using Jeeves-Master at {0}'
