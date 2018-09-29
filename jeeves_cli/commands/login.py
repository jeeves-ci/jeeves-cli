import click
from decorators import with_client

from jeeves_cli.local_storage import storage


@click.command(name='login', help='Login to Jeeves-Master API')
@click.option('-p', '--public-ip', required=False,
              help='The Jeeves-Master public IP.')
@click.option('-u', '--username', required=True,
              help='The Jeeves-Master email address')
@click.option('-p', '--password', required=True,
              help='The Jeeves-Master password')
@with_client
def login(public_ip, username, password, client):
    print 'Logging in...'
    if public_ip is None:
        public_ip = storage.get_master_ip()
    else:
        storage.set_master_ip(public_ip)

    res, _ = client.login.login(username=username, password=password)
    storage.set_access_token(res.access_token)

    print 'Jeeves CLI logged in to Jeeves-Master at {}'.format(public_ip)
