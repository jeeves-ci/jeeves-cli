import click
from decorators import with_client

from jeeves_cli.local_storage import storage
from jeeves_cli.exceptions import CLIParameterException


@click.command(name='use', help='Point CLI to use different master IP.')
@click.option('-i', '--ip', required=True,
              help='The Jeeves-Master public IP.')
@click.option('-u', '--username', required=True,
              help='The Jeeves-Master email address')
@click.option('-p', '--password', required=True,
              help='The Jeeves-Master password')
@click.option('-f', '--force', required=False, is_flag=True,
              help='Force flag.')
@with_client
def use(ip, username, password, force, client):
    print 'Initializing Jeeves CLI\'s local env.'
    master_ip = storage.get_master_ip()
    if master_ip and not force:
        raise CLIParameterException('A local jeeves already exists.'
                                    'Use the \'jvc init\' command.')
    storage.set_master_ip(ip)

    if username and password:
        res, _ = client.login.login(username=username, password=password)
        storage.set_access_token(res.access_token)

    print 'Jeeves CLI now using Jeeves-Master at {0}'.format(ip)
