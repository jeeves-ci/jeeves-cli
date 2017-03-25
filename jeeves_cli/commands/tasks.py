from decorators import with_client
from jeeves_cli import utils

import click


@click.group('tasks', help='Task operations.')
def tasks():
    pass


@click.command(name='list',
               help='List all Jeeves tasks by workflow id.')
@click.option('-w', '--workflow-id', required=True,
              help='The workflow tag ID for the Jeeves tasks.')
@click.option('--verbose', '-v', is_flag=True, help='All task data.',
              default=False)
@with_client
def list(workflow_id, verbose, client):
    tasks_list, _ = client.tasks.list(workflow_id)
    if not verbose:
        for task in tasks_list:
            print task.id
    else:
        _print_workflow_data(tasks_list)


def _print_workflow_data(tasks_list):
    headers = ['Task-id', 'Name', 'Status', 'Minion-IP', 'Started-at']
    keys = ['task_id', 'task_name', 'status', 'minion_ip', 'started_at']
    print utils.format_as_table(data=tasks_list, keys=keys, header=headers)
