import os

import click

from jeeves_cli.constants import (MINION_LOGS_PATH,
                                  MASTER_LOG_FILE)
from jeeves_cli.exceptions import CLIParameterException
from jeeves_cli.local_storage import storage


@click.command(name='init', help='Initialize local Jeeves work environment.')
@click.option('-p', '--project-root', required=False,
              help='Path to project root directory. For example '
                   '\'~/dev/jeeves-ci\'')
def init(project_root):
    print 'Initializing Jeeves CLI\'s local env.'
    local_data = storage.get_local_data()
    if not local_data:
        if not project_root:
            raise CLIParameterException('a Path to project root directory '
                                        'must be provided. For example: '
                                        '\'~/dev/jeeves-ci\'')
        else:
            if _get_missing_sources():
                raise CLIParameterException('Jeeves-CI project could not'
                                            ' be found in {0}'.format(
                                                os.path.abspath(project_root)))
            storage.init_local_storage(os.path.abspath(project_root))
    elif project_root:
        storage.set_project_root(os.path.abspath(project_root))

    # Create client and server log dirs on host
    if not os.path.isdir(MINION_LOGS_PATH):
        os.mkdir(MINION_LOGS_PATH)
    if not os.path.isdir(MASTER_LOG_FILE):
        os.mkdir(os.path.dirname(MASTER_LOG_FILE))

    print 'Time-Sync CLI environment initialized successfully.'


def _get_missing_sources():
    return None
