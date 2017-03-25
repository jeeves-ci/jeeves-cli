from jeeves_cli.commands import use
from jeeves_cli.commands import init
from jeeves_cli.commands import teardown
from jeeves_cli.commands import bootstrap
from jeeves_cli.commands import workflows
from jeeves_cli.commands import tasks

import click


@click.group('jvc')
def _jvc():
    pass


def _add_commands():
    _jvc.add_command(init.init)
    _jvc.add_command(use.use)

    _jvc.add_command(bootstrap.bootstrap)
    _jvc.add_command(bootstrap.bootstrap_local)

    _jvc.add_command(workflows.workflows)
    workflows.workflows.add_command(workflows.upload)
    workflows.workflows.add_command(workflows.revoke)
    workflows.workflows.add_command(workflows.list)
    workflows.workflows.add_command(workflows.get)

    _jvc.add_command(tasks.tasks)
    tasks.tasks.add_command(tasks.list)

    _jvc.add_command(teardown.teardown)


_add_commands()

if __name__ == '__main__':
    _jvc()
