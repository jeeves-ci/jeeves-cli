import click

from jeeves_cli.bootstraper import JeevesBootstrapper
from jeeves_cli.local_storage import storage


@click.command(name='teardown', help='Teardown the Time-Sync application.')
def teardown():
    bootstrapper = JeevesBootstrapper()
    bootstrapper.teardown()
    if storage.get_local_data():
        storage.set_rabbitmq_ip('')
        storage.set_postgres_ip('')
        storage.set_master_ip('')
