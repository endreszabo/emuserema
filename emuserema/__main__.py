#!/usr/bin/env python3

from emuserema import Emuserema
from sys import argv
from argparse import ArgumentParser


def main(args=None):
    """Main entry point."""
    if args is None:
        args = argv[1:]

    parser = ArgumentParser()
    parser.add_argument("-c", "--config-dir",
            help="Directory of configurations", type=str)
    parser.add_argument("-i", "--init",
            help="Make initial configurations",
            action="store_true")
    parser.add_argument("-t", "--test",
            help="Only test configurations and exit.",
            action="store_true")
    parser.add_argument("-d", "--dump",
            help="Dump parsed world configuration YAML.",
            action="store_true")
    args = parser.parse_args()

    if args.init:
        from emuserema.utils import generate_initial_config
        generate_initial_config(args.config_dir)
        exit(0)

    emuserema = Emuserema(
        definitions_directory=args.config_dir
    )

    if args.dump:
        emuserema.dump()
    if args.test:
        print("Configuration parsing was successful.")
        exit(0)

    emuserema.render()


if __name__ == '__main__':
    main()
