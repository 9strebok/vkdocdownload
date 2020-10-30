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


def green_paint_with_output(text: str, output):
    output = str(output)
    return f"{Fore.GREEN}{text}{Style.RESET_ALL} {output}"


def green_paint_with_output_reverse(text: str, output):
    output = str(output)
    return f"{text}{Fore.GREEN} {output}{Style.RESET_ALL}"


def red_paint(text: str):
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def red_paint_with_output(text: str, output):
    output = str(output)
    return f"{Fore.RED}{text}{Style.RESET_ALL} {output}"


def red_paint_with_output_reverse(text: str, output):
    output = str(output)
    return f"{text}{Fore.RED} {output}{Style.RESET_ALL}"


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
        help = "python3 vkdocdownloader.py --settings [SETTINGS_FILE]",
        default = "settings.ini"
    )

    return args_parser.parse_args()
def get_user_token(settings: str):
    app_id = input(
            green_paint("Enter vk app ID: ")
    )

    params = {
        'client_id':       app_id,
        'display':         'page',
        'redirect_uri':    'https://oauth.vk.com/blank.html',
        'scope':           'docs,offline',
        'response_type':   'token',
        'v':               5.68
    }

    url = f"https://oauth.vk.com/authorize?{urlencode(params)}"
    webbrowser.open(url)

    token = input(green_paint("Parse your access token there: "))

    print(
        green_paint_with_output("Saving your App ID and TOKEN in", settings)
    )

    config = ConfigParser()
    config.add_section("SETTINGS")
    config.set("SETTINGS", "app_id", app_id)
    config.set("SETTINGS", "user_token", token)
    settigns_path = Path(settings)
    with settigns_path.open(mode = "w") as settings_file:
        config.write(settings_file)

    return token


class VkDocument:

    def __init__(self, data):
        self.id = data['id'] # File ID
        self.owner_id = data['owner_id'] # File owner ID
        self.title = data['title'] # File name
        self.size = data['size'] # File size in bytes
        self.ext = data['ext'] # File extension
        self.url = data['url'] # File url
        self.add_date = data['date'] # Date


    def __str__(self):
        title    = self.title
        doc_id   = self.id
        owner    = self.owner_id
        add_date = date.fromtimestamp(self.add_date)
        B        = self.size
        KB       = round(self.size/(2**10), 2)
        MB       = round(self.size/(2**20), 2)

        return f"""
{green_paint('Title:')}\t         {title}
{green_paint('ID:')}\t         {doc_id}
{green_paint('Owner:')}\t         {owner}
{green_paint('Date of add:')}\t {add_date}
{green_paint('Size:')}\t         {B} Bytes | {KB} KB | {MB} MB
                """

    def download(self, loot_dir):
        doc_id = self.id
        owner  = self.owner_id
        title  = self.title

        filename = f"{doc_id}_{owner}_{title}"

        try:
            data = urlopen(self.url).read()
        except Exception:
            pass

        Path(loot_dir+"/"+filename).write_bytes(data)
        return green_paint_with_output("Saved:", filename)


def search_docs(query, token):
    params = {
        'q':            query,
        'count':        1000,
        'access_token': token,
        'v':            5.68
    }
    url = f'https://api.vk.com/method/docs.search?{urlencode(params)}'
    response = urlopen(url)
    data = json.loads(response.read().decode())

    if 'error' in data and data['error']['error_code'] == 5:
        print(
            red_paint(f"Invalid user token. Try to get new. Delete settings file and restart")
        )
        exit(1)
    else:
        docs = [VkDocument(item) for item in data['response']['items']]
        return docs


def printTotalInfo(docs):
    total_size = sum([doc.size for doc in docs])
    nfiles     = len(docs)
    B          = total_size
    KB         = round(total_size/(2**10), 2)
    MB         = round(total_size/(2**20), 2)
    GB         = round(total_size/(2**30), 2)

    t = green_paint_with_output("\nTotal files:", str(nfiles))
    z = green_paint_with_output("\nTotal size: ", f"{str(B)} Bytes | {str(KB)} KB | {str(MB)} MB | {str(GB)} GB")

    print(t+z)



def downloadDocs(docs, nthreads, loot_dir):
    with ThreadPoolExecutor(max_workers=nthreads) as executor:
        futures = [executor.submit(doc.download, loot_dir) for doc in docs]
        for future in as_completed(futures):
            try:
                print(future.result())
            except Exception:
                raise Exception



def main():
    BANNER = """HHHHHHHHH"""
    DESC = "Search and download vk.com documents"
    args = parse_args(DESC)

    QUERY = args.query
    SAVE = args.save
    EXTENSIONS = args.extensions
    LOOT_DIR = args.path
    THREADS = args.threads
    SETTINGS_FILE = Path(args.settings)


    if not SETTINGS_FILE.exists():
        TOKEN = get_user_token(SETTINGS_FILE)
    else:
        config = ConfigParser()
        with SETTINGS_FILE.open() as sf:
            config.read_file(sf)
        TOKEN = config.get("SETTINGS", "user_token")
    print(green_paint("OK"))
    print(green_paint("Searching..."))

    docs = search_docs(QUERY, TOKEN)

    if EXTENSIONS:
        docs = list(filter(lambda doc: doc.ext in EXTENSIONS, docs))

    docs.sort(key=lambda doc: doc.add_date, reverse=True)
    [print(green_paint(doc)) for doc in docs]
    printTotalInfo(docs)

    if SAVE:
        loot_path = Path(LOOT_DIR)
        if not loot_path.exists() or not loot_path.is_dir():
            loot_path.mkdir()
        start = time()

        print(
            green_paint_with_output_reverse("\nStart downloading of found files at:", str(ctime(start)))
        )

        downloadDocs(docs, THREADS, LOOT_DIR)
        finish = time()
        d = ctime(finish)
        ttime = timedelta(seconds = finish - start)
        print(
            green_paint_with_output_reverse("Finish_at:", str(d)),
            green_paint_with_output_reverse("Total time:", str(ttime))
        )


if __name__ == "__main__":
    main()