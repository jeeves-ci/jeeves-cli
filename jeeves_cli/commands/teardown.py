import click

from jeeves_cli.bootstraper import JeevesBootstrapper
from jeeves_cli.local_storage import storage


@click.command(name='teardown', help='Terminate all Jeeves components')
def teardown():
    bootstrapper = JeevesBootstrapper()
    bootstrapper.teardown()
    if storage.get_local_data():
        storage.init_local_storage()
