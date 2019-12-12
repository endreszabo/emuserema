#!/usr/bin/env python3

from emuserema import Emuserema
from sys import argv
from argparse import ArgumentParser


def main(args=None):
    """Main entry point."""
    if args is None:
        args = argv[1:]

    parser = ArgumentParser()
    parser.add_argument("-t", "--test",
            help="Only test configurations and exit.",
            action="store_true")
    args = parser.parse_args()

    emuserema = Emuserema()

    if args.test:
        print("Configuration parsing was successful.")
        exit(0)

    emuserema.render()


if __name__ == '__main__':
    main()
