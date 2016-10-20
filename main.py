#!/usr/bin/python3
from argparse import ArgumentParser
from os.path import isfile
from sys import exit
import json

def runServer():
    parser = ArgumentParser(description = "Real Advenced tftp server")
    parser.add_argument("--conf", required=True, help="config file to load")
    parser.add_argument("--foreground", help="launch server on interactive mode")
    arg = parser.parse_args()

    if not isfile(arg.conf):
        print("unexistant config file")
        return 1
    with open(arg.conf, "r") as fd:
        config = json.load(fd)

if __name__ == "__main__":
    exit(runServer())
