"""The watch command for corrcli.

Launch a deamon that will watch for command line programs launched
with the given ID.

    $ corrcli watch start
    [ID]

Stop the deamon.

    $ corrcli watch stop [ID]

"""

import click
from ..watcher import Watcher
from .cli import cli
from ..job_manager import job_manager_callback


@cli.group()
def watch():
    """Launch a deamon for watching other processes.
    """

def test_callback(watcher_id, config_dir, logger=None):
    """Callback function to test the watcher launcher.

    It writes to the log file and waits to be shutdown.

    Args:
      watcher_id: the ID of watcher running the callback
      config_dir: the CoRR configuration directory
      logger: a logger object to write log messages

    >>> test_callback(1, '/fake/directory', logger=...)

    """
    if logger:
        logger.info("in callback for watcher {0} and config directory {1}".format(watcher_id,
                                                                                  config_dir))
    from time import sleep
    while True:
        sleep(10)

def test_callback_nosleep(watcher_id, config_dir, logger=None):
    """Callback that exits for testing purposes.

    Args:
      watcher_id: the ID of watcher running the callback
      config_dir: the CoRR configuration directory
      logger: a logger object to write log messages

    """
    if logger:
        logger.info("in callback for watcher {0} and config directory {1}".format(watcher_id,
                                                                                  config_dir))

CALLBACK_FUNCTIONS = dict((func.__name__, func) for func in (test_callback_nosleep,
                                                             job_manager_callback,
                                                             test_callback))

@watch.command()
@click.option('--log/--no-log',
              default=False,
              help="Whether to record the output of the watcher watcher")
@click.option('--callback-func',
              'callback_func_key',
              default=job_manager_callback.__name__,
              help="The callback function to use (only for testing purposes).",
              type=click.Choice(CALLBACK_FUNCTIONS.keys()))
@click.option('--daemon/--no-daemon',
              'daemon_on',
              default=True,
              help="Whether to run the watcher as a daemon process (only for testing purposes)")
@click.pass_context
def start(ctx, log, callback_func_key, daemon_on):
    """Launch a Watcher to watch processes.
    """
    config_dir = ctx.parent.parent.params['config_dir']
    callback_func = CALLBACK_FUNCTIONS[callback_func_key]
    watcher = Watcher(callback_func, config_dir, daemon_on, logging_on=log)
    click.echo("Launch watcher with ID: {0}".format(watcher.watcher_id))
    if log:
        click.echo("Writing logs to {0}".format(watcher.log_file))
    watcher.start()

@watch.command()
@click.option('--all', 'all_watchers', is_flag=True, help="Stop all watcher watchers.")
@click.argument('watcher_ids', nargs=-1)
@click.pass_context
def stop(ctx, all_watchers, watcher_ids):
    """Shut down watching watchers.
    """
    config_dir = ctx.parent.parent.params['config_dir']
    if (not all_watchers) and len(watcher_ids) == 0:
        click.echo("Require a watcher ID to proceed.")
    else:
        stopped_df = Watcher.stop(watcher_ids=watcher_ids,
                                  all_watchers=all_watchers,
                                  config_dir=config_dir)
        if len(stopped_df) > 0:
            click.echo("Stopping watchers.")
            for _, row in stopped_df.iterrows():
                click.echo("Stopped {0} with pid {1}".format(row.watcher_id, row.process_id))
        else:
            click.echo("No watchers stopped.")


@watch.command('list')
@click.pass_context
def list_watchers(ctx):
    """List all Watchers.
    """
    config_dir = ctx.parent.parent.params['config_dir']
    watcher_df = Watcher.list(config_dir=config_dir).set_index('watcher_id')
    if len(watcher_df) == 0:
        click.echo("No running watchers.")
    else:
        click.echo(watcher_df)
