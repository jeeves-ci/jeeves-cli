from decorators import with_client
from jeeves_cli import utils

import click

from jeeves_rest_client.rest_client_exceptions import JeevesHttpError

from jeeves_cli.exceptions import CLIRestException


@click.group('tasks', help='Workflow Task operations.')
def tasks():
    pass


@click.command(name='list',
               help='List all Jeeves tasks by workflow id.')
@click.option('-w', '--workflow-id', required=True,
              help='The workflow tag ID for the Jeeves tasks.')
@click.option('--page', '-p', help='List paginated response', default=0)
@click.option('--size', '-s', help='List result size', default=100)
@click.option('--verbose', '-v', is_flag=True, help='All task data.',
              default=False)
@with_client
def list(workflow_id, page, size, verbose, client):
    try:
        tasks_list, _ = client.tasks.list(workflow_id, page=page, size=size)
    except JeevesHttpError as e:
        raise CLIRestException(e.message)

    if not verbose:
        for task in tasks_list.tasks:
            print task.task_id
    else:
        _print_workflow_data(tasks_list.tasks)


def _print_workflow_data(tasks_list):
    headers = ['Task-ID', 'Name', 'Status', 'Minion-IP', 'Started-At']
    keys = ['task_id', 'task_name', 'status', 'minion_ip', 'started_at']
    print utils.format_as_table(data=tasks_list, keys=keys, header=headers)
