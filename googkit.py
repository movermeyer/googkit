import os
import sys
from lib.command import CommandParser
from lib.config import Config
from lib.environment import Environment
from lib.error import GoogkitError


PROJECT_CONFIG = 'googkit.cfg'
USER_CONFIG = '.googkit'
DEFAULT_CONFIG = 'config/default.cfg'

# It makes unit-testing easy
GLOBAL = { 'ENV': os.environ }


def print_help(args=[]):
    right_commands = CommandParser.right_commands(args)
    if len(right_commands) == 0:
        print('Usage: googkit <command>')
    else:
        print('Usage: googkit %s <command>' % (' '.join(right_commands)))

    print('')
    print('Available commands:')

    available_commands = CommandParser.available_commands(right_commands)
    for name in available_commands:
        print('    ' + name)


def googkit_root():
    googkit_home_path = GLOBAL['ENV'].get('GOOGKIT_HOME')
    if googkit_home_path is None:
        raise GoogkitError('Missing environment variable: "GOOGKIT_HOME"')

    if not os.path.exists(googkit_home_path):
        raise GoogkitError('googkit directory is not found: %s' % googkit_home_path)

    return os.path.expanduser(googkit_home_path)


def project_root():
    current = os.getcwd()
    try:
        while not os.path.exists(os.path.join(current, PROJECT_CONFIG)):
            before = current
            current = os.path.abspath(os.path.join(current, '../'))

            # Break if current smeems root.
            if before == current:
                current = None
                break

        return current
    except IOError:
        return None


def project_config_path():
    proj_root = project_root()

    if proj_root is None:
        raise GoogkitError('Project directory is not found.')

    project_config = os.path.join(proj_root, PROJECT_CONFIG)

    if not os.path.exists(project_config):
        raise GoogkitError('Project config file is not found.')

    return project_config


def user_config_path():
    home_dir = os.path.expanduser('~')
    user_config = os.path.join(home_dir, USER_CONFIG)

    return user_config if os.path.exists(user_config) else None


def default_config_path():
    googkit_home_path = googkit_root()
    default_config = os.path.join(googkit_home_path, DEFAULT_CONFIG)

    if not os.path.exists(default_config):
        raise GoogkitError('Default config file is not found: %s' % default_config)

    return default_config


def find_config():
    default_config = default_config_path()
    user_config = user_config_path()
    project_config = project_config_path()

    config = Config()
    config.load(project_config, user_config, default_config)
    return config


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit()

    args = sys.argv[1:]
    classes = CommandParser.command_classes(args)
    if classes is None:
        print_help(args)
        sys.exit()

    try:
        config = None
        for cls in classes:
            if config is None and cls.needs_config():
                config = find_config()

            env = Environment(args, config)
            command = cls(env)
            command.run()
    except GoogkitError:
        sys.exit('[ERROR] ' + str(e))
