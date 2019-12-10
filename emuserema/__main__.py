#!/usr/bin/env python3

from emuserema import Emuserema
from sys import argv
from IPython import embed


def main():
    emuserema = Emuserema()
    if len(argv) > 1:
        if argv[1] == '-t':
            print("Configuration parsing was successful.")
            exit(0)
    embed()
    emuserema.render()


if __name__ == '__main__':
    main()
