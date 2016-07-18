"""The config commands for `corrcli`
"""
import os

from configparser import ConfigParser
import click

from .cli import cli
from .cli import DEFAULT_CONFIG_FILE


@cli.group()
def config():
    """Configure the CoRR command line tool.
    """

@config.command('set')
@click.option('--email', default=None, help="Add email address.", type=str)
@click.option('--author', default=None, help="Add author's name.", type=str)
@click.option('--watch-refresh-rate',
              default=None,
              help="The refresh rate for watching jobs.",
              type=float)
@click.option('--write-refresh-rate',
              default=None,
              help="The refresh rate for writing jobs.",
              type=float)
@click.pass_context
def set_config(ctx, email, author, watch_refresh_rate, write_refresh_rate):
    """Write data to the 'config.ini' file.
    """
    config_dir = ctx.parent.parent.params.get('config_dir') or \
                 ctx.parent.parent.parent.params.get('config_dir')

    ini_file = os.path.join(config_dir, DEFAULT_CONFIG_FILE)

    entries = [('global', 'email', email),
               ('global', 'author', author),
               ('jobs', 'write_refresh_rate', write_refresh_rate),
               ('jobs', 'watch_refresh_rate', watch_refresh_rate)]

    for section, key, value in entries:
        write_item(ini_file, section, key, value)


@config.command('list')
@click.pass_context
def list_config(ctx):
    """List contents of the config file.
    """
    config_dir = ctx.parent.parent.params['config_dir']
    ini_file = os.path.join(config_dir, DEFAULT_CONFIG_FILE)
    ctx.invoke(set_config)
    with open(ini_file, 'r') as fpointer:
        click.echo(fpointer.read())

@config.command()
@click.pass_context
def edit(ctx): # pragma: no cover
    """Edit the contents of the config file.
    """
    config_dir = ctx.parent.parent.params['config_dir']
    ini_file = os.path.join(config_dir, DEFAULT_CONFIG_FILE)
    ctx.invoke(set_config)
    click.edit(filename=ini_file)

def write_item(ini_file, section, key, value=None):
    """Write a key value pair to an ini file.

    Write the following to a file.

    ```
    [section]
    key = value
    ```

    Args:
      ini_file: the config file to write to
      section: the `[section]` to write to
      key: the key in `key = value`
      value: the value in `key = value`

    """
    parser = ConfigParser()
    parser.read(ini_file)
    if not parser.has_section(section):
        parser.add_section(section)
        click.echo("Write '[{section}]' to {config_ini}.".format(section=section,
                                                                 config_ini=ini_file))
    if value:
        parser.set(section, key, str(value))
        click.echo("Write '{key} = {value}' to {config_ini}.".format(key=key,
                                                                     value=value,
                                                                     config_ini=ini_file))
    with open(ini_file, 'w') as fpointer:
        parser.write(fpointer)

def parse_config(config_dir):
    """Parse the configuration file.

    Using a dictionary is easier than using the ConfigParser directly.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> ini_contents = '[default]\\nvalue = 0'
    >>> with runner.isolated_filesystem() as config_dir:
    ...     config_file = os.path.join(config_dir, 'config.ini')
    ...     with open(config_file, 'w') as fout:
    ...         _ = fout.write(ini_contents)
    ...     assert parse_config(config_dir) == {'default_value' : '0'}

    Args:
      config_dir: the CoRR configuration directory

    Returns:
      a dictionary of the form `section_option : value`.

    """
    parser = ConfigParser()
    parser.read(os.path.join(config_dir, DEFAULT_CONFIG_FILE))
    data = {}
    for section in parser.sections():
        for option in parser.options(section):
            data["{0}_{1}".format(section, option)] = parser.get(section, option)
    return data
