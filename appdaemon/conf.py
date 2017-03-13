import configparser
import logging
import os
import threading

ha_url = ""
ha_key = ""
app_dir = ""
threads = 0
monitored_files = {}
modules = {}

# Will require object based locking if implemented
objects = {}

schedule = {}
schedule_lock = threading.RLock()

callbacks = {}
callbacks_lock = threading.RLock()

ha_state = {}
ha_state_lock = threading.RLock()

# No locking yet
global_vars = {}

sun = {}
config = None
location = None
tz = None
logger = logging.getLogger(__name__)
now = 0
tick = 1
realtime = True
timeout = 10
endtime = None
interval = 1
certpath = None

loglevel = "INFO"
ha_config = None
version = 0
commtype = None


_DEPRECATED_CONFIG_ENTRIES = {
    'elevation', 'latitude', 'longitude', 'timezone', 'time_zone'}

app_daemon_config = None


def configure(command_line):
    global app_daemon_config

    if app_daemon_config is None:
        app_daemon_config = AppDaemonConfig(command_line)
        assert app_daemon_config.valid, "[AppDaemon] section required in {}"\
            .format(app_daemon_config.config_file)
        app_daemon_config.init_legacy_config()


class AppDaemonConfig:

    def __init__(self, command_line):
        self._command_line = command_line
        self._config_file = self._find_path(self._command_line.config_file)

        self._config_parser = configparser.ConfigParser()
        self._config_parser.read(self.config_file)

    def init_legacy_config(self):
        global loglevel
        global config, ha_url, ha_key, logfile, errorfile, app_dir, threads
        global certpath

        loglevel = self._command_line.log_level
        config = self._config_parser
        ha_url = config['AppDaemon']['ha_url']
        ha_key = config['AppDaemon'].get('ha_key', "")
        logfile = config['AppDaemon'].get("logfile")
        errorfile = config['AppDaemon'].get("errorfile")
        app_dir = config['AppDaemon'].get("app_dir")
        threads = int(config['AppDaemon']['threads'])
        certpath = config['AppDaemon'].get("cert_path")

    @property
    def daemon(self):
        return self._command_line.daemon

    @property
    def config_dir(self):
        return self._command_line.config_dir

    @property
    def config_file(self):
        return self._config_file

    @property
    def dependencies(self):
        return self._config_parser['dependencies']

    @property
    def valid(self):
        return self._config_parser.has_section('AppDaemon')

    def log_deprecated_entries(self, ha_log):
        for key in _DEPRECATED_CONFIG_ENTRIES:
            if key in self._config_parser['AppDaemon']:
                ha_log(logger, "WARNING",
                       "'{}' directive is deprecated, please remove"
                        .format(key))

    def _find_path(self, name):
        if os.path.isabs(name):
            if os.path.isfile(name):
                return name
            else:
                raise ValueError("{} does not exist".format(name))

        if self.config_dir is None:
            raise ValueError(
            ("Not looking up {}. " +
             "No config dir specified and default locations aren't present.")
                .format(name))

        _file = os.path.join(self.config_dir, name)
        if os.path.isfile(_file) or os.path.isdir(_file):
            return _file

        raise ValueError(
                "Cannot find {} in {}.".format(name, self.config_dir)
        )
