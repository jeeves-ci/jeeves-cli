import os
import yaml
import json

from decorators import with_client
from jeeves_cli import utils

import click

from jeeves_commons.dsl import validate
from jeeves_cli.exceptions import CLIParameterException, CLIRestException
from jeeves_rest_client.rest_client_exceptions import JeevesHttpError


@click.group('workflows', help='Workflow operations.')
def workflows():
    pass


@click.command(name='upload',
               help='Upload a jeeves.yaml Workflow.')
@click.option('-p', '--path', required=True,
              help='The path to the jeeves.yaml file.')
@click.option('-t', '--tag', required=False,
              help='The tag ID for the Jeeves workflow. If not specified, '
                   'a unique tag ID will be assigned by the Jeeves-Master.')
@click.option('-e', '--env', required=False, default='{}',
              help='Environment vars associated with the Jeeves workflow.')
@with_client
def upload(path, tag, env, client):
    if not os.path.isfile(path):
        raise CLIParameterException('Path must point to a jeeves.yaml file.')
    with open(path) as f:
        workflow = yaml.load(f)
    try:
        validate.validate_workflow(workflow)
    except validate.ValidationError as e:
        raise CLIParameterException('Jeeves yaml is invalid. Error is: {}'
                                    .format(e.message))
    try:
            env = json.loads(env)
    except ValueError:
        raise CLIParameterException('Jeeves env must be a valid JSON.')
    try:
        workflow, _ = client.workflows.upload(workflow, env or {},
                                              workflow_id=tag)
    except JeevesHttpError as e:
        raise CLIRestException(e.message)

    print 'Workflow with ID \'{0}\' successfully uploaded. Status is \'{1}\'.'\
          .format(workflow.workflow_id, workflow.status)


@click.command(name='revoke',
               help='Revoke a Jeeves Workflow.')
@click.option('-t', '--tag-id', required=True,
              help='The tag ID for the Jeeves workflow.')
@with_client
def revoke(tag_id, client):
    client.workflows.terminate(tag_id)
    print 'Workflow with ID \'{0}\' was successfully revoked.'.format(tag_id)


@click.command(name='get',
               help='Get a Jeeves Workflow by ID.')
@click.option('-t', '--tag-id', required=True,
              help='The tag ID for the Jeeves workflow. If not specified, '
                   'a unique tag ID will be assigned by the Jeeves-Master.')
@with_client
def get(tag_id, client):
    workflow = [client.workflows.get(tag_id)]
    _print_workflow_data(workflow)


@click.command(name='list',
               help='List all Jeeves Workflow by ID.')
@click.option('--verbose', '-v', is_flag=True, help='All workflow data.',
              default=False)
@with_client
def list(verbose, client):
    workflows, _ = client.workflows.list()
    if not verbose:
        for workflow in workflows:
            print workflow.workflow_id
    else:
        _print_workflow_data(workflows)


def _print_workflow_data(workflows):
    headers = ['Workflow-ID', 'Status', 'Started-At', 'Ended-At']
    keys = ['workflow_id', 'status', 'started_at', 'ended_at']
    print utils.format_as_table(data=workflows, keys=keys, header=headers)
