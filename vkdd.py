from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from configparser import ConfigParser
from datetime import date, timedelta
import json
from pathlib import Path
from time import time, ctime

from colorama import Fore, Style
from urllib.parse import urlencode
from urllib.request import urlopen
import webbrowser

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


class VkDocument:
    """
    VK DOCUMENT
    """
    def __init__(self, data: dict):
        self.identificator = data['id'] # File ID
        self.owner_id = data['owner_id'] # File owner ID
        self.title = data['title'] # File name
        self.size = data['size'] # File size in bytes
        self.ext = data['ext'] # File extension
        self.url = data['url'] # File url
        self.add_date = data['date'] # Date


    def __str__(self):
        title = self.title
        doc_id = self.identificator
        owner = self.owner_id
        add_date = date.fromtimestamp(self.add_date)
        B = self.size
        KB = round(self.size/(2**10), 2)
        MB = round(self.size/(2**20), 2)

        return f"""
{green_paint('Title:')}\t         {title}
{green_paint('ID:')}\t         {doc_id}
{green_paint('Owner:')}\t         {owner}
{green_paint('Date of add:')}\t {add_date}
{green_paint('Size:')}\t         {B} Bytes | {KB} KB | {MB} MB 
"""


    def download(self, loot_dir: str):
        """
        def download(self, loot_dir: str)

        Try to download a some VkDocument to {loot_dir}
        Else to log Error with file_name

        """
        owner = self.owner_id
        title = self.title
        saving_file_name = f"{owner}_{title}"

        try:
            data = urlopen(self.url).read()
        except:
            print(red_paint_with_output("ERROR:", "WITH URLOPEN"))

        try:
            Path(loot_dir + "/" + saving_file_name).write_bytes(data)
            return green_paint_with_output("Saved:", title)
        except:
            return red_paint_with_output("ERROR:", title)


def parse_args(desc: str):
    """
    Usage:
        args = parse_args()
        number_of_threads = args.threads

    Realisation:
    def parse_args(desc: str)
        Parsing cl arguments and add --help

        Flags:
            -s/--searches   - Search queries    - type [str]
            --save          - Save or not       - type bool
            -p/--path       - Save path         - type str
            -t/--threads    - Number of threads - type int
            -e/--extensions - Extension list    - type [str]
            --settings      - Settings file     - type str

        return args_parser.parse_args()

    """
    args_parser = ArgumentParser(desc)
    # Search query: [str] => args.search
    args_parser.add_argument(
        "-s", "--searches",
        help = "python3 vkdd.py [Flags] [Search queries]",
        action = "store",
        nargs = "+"
    )
    # Save: bool => args.save
    args_parser.add_argument(
        "--save",
        help = "python3 vkdd.py -s [Search queries] --save",
        action = "store_true"
    )
    # Extensions: [str] => args.extensions
    args_parser.add_argument(
        "-e", "--extensions",
        help = "python3 vkdd.py -e [pdf, doc, jpeg..]",
        nargs = "+",
        default = [],
    )
    # Path: str => args.path
    args_parser.add_argument(
        "-p", "--path",
        help = "python3 vkdd.py -p [PATH_TO_FOLDER] [Query]",
        default = "./loot/"
    )
    # Threads: int => args.threads
    args_parser.add_argument(
        "-t", "--threads",
        help = "python3 vkdd.py -t [NUMBER_OF_THREADS_USED]",
        type = int,
        default = 2
    )
    # Settings: str => args.settings
    args_parser.add_argument(
        "--settings",
        help = "python3 vkdd.py --settings [SETTINGS_FILE]",
        default = "settings.ini"
    )
    return args_parser.parse_args()


def get_user_token(settings_file: str):
    """
    def get_user_token(settings_file: str)
        Ask a vk app id and token

    return {token}

    """

    app_id = input(green_paint("Enter vk app ID: ")).strip()
    params = {
        'client_id': app_id,
        'display': 'page',
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'scope': 'docs,offline',
        'response_type': 'token',
        'v': 5.68
    }
    url = f"https://oauth.vk.com/authorize?{urlencode(params)}"
    webbrowser.open(url)

    token = input(green_paint("Parse your access token there: ")).strip()
    print(green_paint_with_output("Saving your App ID and TOKEN in", settings_file))

    config = ConfigParser()
    config.add_section("SETTINGS")
    config.set("SETTINGS", "app_id", app_id)
    config.set("SETTINGS", "user_token", token)
    settigns_path = Path(settings_file)

    with settigns_path.open(mode = "w") as settings:
        config.write(settings)
    return token


def search_docs(query: str, token: str):
    """
    def search_docs(query: str, token: str)

    """
    params = {
        'q': query,
        'count': 1000,
        'access_token': token,
        'v': 5.68
    }

    url = f'https://api.vk.com/method/docs.search?{urlencode(params)}'
    response = urlopen(url)
    data = json.loads(response.read().decode())

    if 'error' in data and data['error']['error_code'] == 5:
        print(red_paint("Invalid user token. Try to get new. Delete settings file and restart"))
        exit(1)
    else:
        docs = [VkDocument(item) for item in data['response']['items']]
        return docs


def print_total_info(docs: VkDocument):
    """
    def print_total_info(docs: VkDocument)

    print:
        Total files: files_lenth
        Total size: {B} B | {KB} KB | {MB} MB | {GB} GB

    """

    total_size = sum([doc.size for doc in docs])
    files_length = len(docs)
    B = total_size
    KB = round(total_size/(2**10), 2)
    MB = round(total_size/(2**20), 2)
    GB = round(total_size/(2**30), 2)

    files = green_paint_with_output("\nTotal files:", files_length)
    size = green_paint_with_output("\nTotal size: ", f"{str(B)} Bytes | {str(KB)} KB | \
{str(MB)} MB | {str(GB)} GB")
    print(files, size)


def download_docs(docs: list, threads_count: int, loot_dir: str):
    with ThreadPoolExecutor(max_workers = threads_count) as executor:
        futures = [executor.submit(doc.download, loot_dir) for doc in docs]
        for future in as_completed(futures):
            try:
                print(future.result())
            except KeyboardInterrupt:
                exit()
            except Exception as error:
                raise error


def vkdd(query: str, token: str, loot_dir: str,
         threads_count: int,  save: bool, extensions: list):
    """
    def vkdd(query: str)

    """
    docs = search_docs(query, token)
    if extensions:
        docs = list(filter(lambda doc: doc.ext in extensions, docs))

    docs.sort(key=lambda doc: doc.add_date, reverse=True)
    if save:
        loot_path = Path(loot_dir)
        if not loot_path.exists() or not loot_path.is_dir():
            loot_path.mkdir()
        start = time()

        print(
            green_paint_with_output_reverse("\nStart downloading of found files at:",
            str(ctime(start)))
        )

        download_docs(docs, threads_count, loot_dir)
        finish = time()
        d = ctime(finish)
        ttime = timedelta(seconds = (finish - start))

        print(
            green_paint_with_output_reverse("Finish_at:", str(d)),
            green_paint_with_output_reverse("Total time:", str(ttime))
        )

    else:
        print(green_paint("Searching..."))
        for doc in docs:
            print(green_paint(doc))
        print_total_info(docs)




def main():
    BANNER = green_paint(
    r"""
                   ,--.
               ,--/  /|    ,---,        ,---,
       ,---.,---,': / '  .'  .' `\    .'  .' `\
      /__./|:   : '/ / ,---.'     \ ,---.'     \
 ,---.;  ; ||   '   ,  |   |  .`\  ||   |  .`\  |
/___/ \  | |'   |  /   :   : |  '  |:   : |  '  |
\   ;  \ ' ||   ;  ;   |   ' '  ;  :|   ' '  ;  :
 \   \  \: |:   '   \  '   | ;  .  |'   | ;  .  |
  ;   \  ' .|   |    ' |   | :  |  '|   | :  |  '
   \   \   ''   : |.  \'   : | /  ; '   : | /  ;
    \   `  ;|   | '_\.'|   | '` ,/  |   | '` ,/
     :   \ |'   : |    ;   :  .'    ;   :  .'
      '---" ;   |,'    |   ,.'      |   ,.'
            '---'      '---'        '---'

    """
    )

    DESC = "Search and download vk.com documents"
    args = parse_args(DESC)
    QUERIES = args.searches
    SAVE = args.save
    EXTENSIONS = args.extensions
    LOOT_DIR = args.path
    THREADS = args.threads
    SETTINGS_FILE = Path(args.settings)

    print(BANNER)

    # GETTING A TOKEN
    if not SETTINGS_FILE.exists():
        TOKEN = get_user_token(SETTINGS_FILE)
    else:
        config = ConfigParser()
        with SETTINGS_FILE.open() as settings_file:
            config.read_file(settings_file)
        TOKEN = config.get("SETTINGS", "user_token")

    # A RUNNING VKDDs
    for que in QUERIES:
        vkdd(query = que,
             token = TOKEN,
             loot_dir = LOOT_DIR,
             threads_count = THREADS,
             save = SAVE,
             extensions = EXTENSIONS)
        print()


if __name__ == "__main__":
    main()
