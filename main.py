#!/usr/bin/python3
from argparse import ArgumentParser
from os.path import isfile
from sys import exit
import json

from ratftpd.config import Config
from ratftpd.server import RatftpServer

class Ratftpd(object):
    def __init__(self):
        self.parseArg()

    def parseArg(self):
        parser = ArgumentParser(description = "Real Advenced tftp server")
        parser.add_argument("--conf", required=True, help="config file to load")
        parser.add_argument("--foreground", help="launch server on interactive mode")
        arg = parser.parse_args()

        if not isfile(arg.conf):
            print("unexistant config file")
            exit(1)
        with open(arg.conf, "r") as fd:
            configJson = json.load(fd)
        self.config = Config(configJson)

    def run(self):
        server = RatftpServer(self.config.bind,
                              self.config.port,
                              self.config.timeout,
                              self.config.retry)
        try:
            server.run()
        except KeyboardInterrupt:
            server.close()
        

if __name__ == "__main__":
    srv = Ratftpd()
    srv.run()
