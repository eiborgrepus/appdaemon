import argparse
import os
import platform


def default_conf_dir():
    conf_dir_hierarchy = [
        os.path.join(os.path.expanduser("~"), '.appdaemon'),
        os.path.join('/etc', 'appdaemon'),
        os.path.join(os.path.expanduser("~"), ".homeassistant")
    ]

    for folder in conf_dir_hierarchy:
        if os.path.isdir(folder):
            return folder
    return None


class CmdLineParser:

    def __init__(self, version):
        self._args = None
        self._parser = argparse.ArgumentParser()

        self._parser.add_argument(
                "-c", "--config", help="full path to config file",
                type=str, default='appdaemon.cfg'
        )
        self._parser.add_argument(
                "-C", "--config-dir", help="full path to config dir",
                type=str, default=default_conf_dir()
        )
        self._parser.add_argument(
                "-p", "--pidfile", help="full path to PID File",
                default="/tmp/hapush.pid"
        )
        self._parser.add_argument(
                "-t", "--tick",
                help="time in seconds that a tick in the schedular lasts",
                default=1, type=float
        )
        self._parser.add_argument(
                "-s", "--starttime",
                help="start time for scheduler <YYYY-MM-DD HH:MM:SS>",
                type=str
        )
        self._parser.add_argument(
                "-e", "--endtime",
                help="end time for scheduler <YYYY-MM-DD HH:MM:SS>",
                type=str, default=None
        )
        self._parser.add_argument(
                "-i", "--interval",
                help="multiplier for scheduler tick", type=float,
                default=1
        )
        self._parser.add_argument(
                "-D", "--debug", help="debug level", default="INFO",
                choices=[
                    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
                ]
        )
        self._parser.add_argument(
                '-v', '--version', action='version',
                version='%(prog)s ' + version
        )
        self._parser.add_argument(
                '--commtype', help="Communication Library to use",
                default="WEBSOCKETS", choices=["SSE", "WEBSOCKETS"]
        )

        # Windows does not have Daemonize package so disallow
        if platform.system() != "Windows":
            self._parser.add_argument("-d", "--daemon",
                                help="run as a background process",
                                action="store_true")

    def parse_args(self):
        if not self._args:
            self._args = self._parser.parse_args()

        return self._args

    @property
    def config_dir(self):
        args = self.parse_args()
        return args.config_dir

    @property
    def config_file(self):
        args = self.parse_args()
        return args.config

    @property
    def log_level(self):
        args = self.parse_args()
        return args.debug

    @property
    def daemon(self):
        args = self.parse_args()
        return platform.system() != 'Windows' and args.daemon
