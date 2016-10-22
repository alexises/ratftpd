#!/usr/bin/python3
from argparse import ArgumentParser
from os.path import isfile
from sys import exit
import json
import logging

from ratftpd.config import Config
from ratftpd.server import RatftpServer
from ratftpd.daemon import Daemon

class Ratftpd(object):
    def __init__(self):
        self.parseArg()
        self.daemon = Daemon(self.config.pidfile)
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
                              self.config.retry)
        if not self.foreground:
            self.daemon.start()
        try: 
            server.run()
        except KeyboardInterrupt:
            server.close()
        except Exception as e:
            self.f.write(str(e))
        if not self.foreground:
            server.close()
            self.daemon.stop()
        

if __name__ == "__main__":
    srv = Ratftpd()
    srv.run()
