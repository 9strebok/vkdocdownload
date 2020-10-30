from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from configparser import ConfigParser
from datetime import date, timedelta
import json
from pathlib import Path
from time import time, ctime

from colorama import Fore, Back, Style
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
import webbrowser



# Beatify functions
def green_paint(text: str):
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def green_paint_with_output(text: str, output: str):
    return f"{Fore.GREEN}{text}{Style.RESET_ALL} {output}"


def green_paint_with_output_reverse(text: str, output: str):
    return f"{text}{Fore.GREEN} {output}{Style.RESET_ALL}"


# Parsing cl arguments
def parse_args(desc: str):
    args_parser = ArgumentParser(desc)

    # Query: str => args.query
    args_parser.add_argument(
        "query",
        help = "python3 vkdocdownloader.py [Flags] [Search Query]"
    )

    # Save: bool => args.save
    args_parser.add_argument(
        "-s", "--save",
        help = "python3 vkdocdownloader.py -s [Search query]",
        action = "store_true"
    )

    # Extensions: [] => args.extensions
    args_parser.add_argument(
        "-e", "--extensions",
        help = "python3 vkdocdownloader.py -e [pdf, doc, jpeg..]",
        action = "append",
        default = []
    )

    # Path: str => args.path
    args_parser.add_argument(
        "-p", "--path",
        help = "python3 vkdocdownloader.py -p [PATH_TO_FOLDER] [Query]",
        default = "./loot/"
    )

    # Threads: int => args.threads
    args_parser.add_argument(
        "-t", "--threads",
        help = "python3 vkdocdownloader.py -t [NUMBER_OF_THREADS_USED]",
        type = int,
        default = 4
    )

    # Settings: str => args.settings
    args_parser.add_argument(
        "--settings",
        help = "python3 vkdocdownloader.py --settings [SETTINGS_FILE]"
        default = "settings.ini"
    )

    return args_parser.parse_args()


def main():
    DESC = "Search and download vk.com documents"
    args = parse_args(DESC)

    QUERY = args.query
    SAVE = args.save
    EXTENSIONS = args.extensions

    if args.path[-1] == "/":
        LOOT_DIR = args.path
    else:
        LOOT_DIR = args.path + "/"

    THREADS = args.threads
    SETTINGS_FILE = args.settings


if __name__ == "__main__":
    main()
