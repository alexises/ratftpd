#!/usr/bin/python3
# This file is part of Ratftpd.
#
# Ratftpd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ratftpd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ratftpd.  If not, see <http://www.gnu.org/licenses/>.

from argparse import ArgumentParser
from os.path import isfile
from sys import exit
import json
import logging

from ratftpd.config import Config
from ratftpd.server import RatftpServer
from ratftpd.daemon import Daemon

logger = logging.getLogger(__name__)
class Ratftpd(object):
    def __init__(self):
        self.parseArg()
        self.daemon = Daemon(self.config.pidfile, uid=self.config.uid, gid=self.config.gid)
        logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

    def parseArg(self):
        parser = ArgumentParser(description = "Real Advenced tftp server")
        parser.add_argument("--conf", required=True, help="config file to load")
        parser.add_argument("--foreground", default=False, action='store_true', help="launch server on interactive mode")
        arg = parser.parse_args()

        if not isfile(arg.conf):
            print("unexistant config file")
            exit(1)
        with open(arg.conf, "r") as fd:
            configJson = json.load(fd)
        self.foreground = arg.foreground
        self.config = Config(configJson)
        self.config.networks.pretyPrint()

    def run(self):
        server = RatftpServer(self.config.bind,
                              self.config.port,
                              self.config.timeout,
                              self.config.retry,
                              self.config)
        logger.info("listen ok")
        if not self.foreground:
            self.daemon.start()
            logger.info("daemon started")
            self.daemon.dropPrivilege()
            logger.info("drop privilege")
        try:
            logger.info("start server") 
            server.run()
        except KeyboardInterrupt:
            server.close()
        except Exception as e:
            logger.error(str(e))
        if not self.foreground:
            server.close()
            self.daemon.stop()
        

if __name__ == "__main__":
    logger.info("start application")
    srv = Ratftpd()
    srv.run()
