import click

from jeeves_cli.local_storage import storage
from jeeves_cli.exceptions import CLIParameterException


@click.command(name='init', help='Initialize local Jeeves work environment.')
@click.option('--force', '-f', is_flag=True, help='Block tail operation.',
              default=False)
def init(force):
    print 'Initializing Jeeves CLI\'s local env.'
    local_data = storage.get_local_data()
    if not local_data:
        storage.init_local_storage()
    elif not force:
        raise CLIParameterException('A local jeeves env already exists.'
                                    'Use the \'-f\' flag to override it.')

    print 'Jeeves CLI environment initialized successfully.'
