import logging
import os
import argparse
import sys
import bs4
from six.moves.urllib.request import urlopen


class Response(object):
    def __init__(self, response):
        self.__response = response
        self.content = self.__download()
        self.status_code = response.getcode()

    def __download(self, chunk_size=1024):
        content = self.__response.read(chunk_size)
        while True:
            chunk = self.__response.read(chunk_size)
            if len(chunk):
                content += chunk
            else:
                break
        return content

    def close(self):
        self.__response.close()


def get(url):
    return Response(urlopen(url))

# Basic requirements
# -o --output-file

# Cool requirements
# -d --debug (debugging level); Done
# -t --tries=int (number of tries until success of each url); Done (At least for basic mode)
# -O --log-file; Done
# -r --recursive
# -l --level=
# --spider
# --user=
# --password=


# noinspection PyMethodMayBeStatic
class Handler(object):
    def __init__(self):
        self.__base_url = None
        self.__output_file = None
        self.__basic_auth_credentials = None
        self.__spider_mode = None
        self.__recursive_mode = None
        self.__depth_level = None
        self.__tries = None

        self.__sub_urls = []
        self.__sub_urls_visited = []
        self.__formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.__logger = logging.Logger(f"{sys.argv[0]} session")

    # Source: https://stackoverflow.com/a/24856208
    # Check if file content has html
    def __check_html(self, bs4_response: bs4.BeautifulSoup) -> bool:
        return bool(bs4_response.find())

    def __join_url(self, url: str, path: str) -> str:
        url_schema = "https://" if url.startswith("https://") else "http://"
        split_url = url.replace(url_schema, "").split("#")[0].split("?")[0].split("/")
        split_path = path.split("#")[0].split("?")[0].split("/")
        for file in split_path:
            if file == "..":
                if len(split_url) > 1:
                    split_url.pop()
            else:
                split_url.append(file)
        return url_schema + "/".join(split_url)

    def __get_urls_from_page(self, url) -> list:
        urls = []
        response = get(url)
        bs4_response = bs4.BeautifulSoup(response.content, "html.parser")
        if response.status_code in (200, 204, 301, 302, 307, 401, 403):
            if self.__check_html(bs4_response):
                results_iter = bs4_response.findAll()
                for result in results_iter:
                    href_url = result.get("href")
                    src_url = result.get("src")
                    if href_url:
                        urls.append(href_url)
                    if src_url:
                        urls.append(src_url)
        return list(set(filter(lambda sub_url: "#" != sub_url[0], urls)))

    def __download_url_to_file(self, url: str, output_file: str) -> bool:
        success = False
        self.__logger.info(f"Staring the Download of url: {url} to Path: {output_file}")
        try:
            response = get(url)
            with open(output_file, "wb") as output_file_object:
                output_file_object.write(response.content)
                output_file_object.close()
            self.__logger.info(f"URL: {url} Downloaded to: {output_file}")
            response.close()
            success = True
        except Exception as e:
            self.__logger.error(f"Error: {e} While Downloading: {url} to: {output_file}")
        return success

    def __make_request(self, url: str, output_file: str) -> (list or bool):
        for try_ in range(self.__tries):
            self.__logger.debug(f"Try number {try_ + 1} of {self.__tries} tries")
            if self.__spider_mode:
                result = self.__get_urls_from_page(url)
            else:
                result = self.__download_url_to_file(url, output_file)
            if type(result) == bool:
                if result:
                    self.__logger.debug(f"Done at try number {try_ + 1} of {self.__tries} tries")
                    return result
            else:
                return result

    def __get_filename_from_url(self, url: str) -> str:
        split_url = url.split("#")[0].split("?")[0].split("/")
        filename = split_url[-2] if split_url[-1] == "" else split_url[-1]
        self.__logger.debug(f"Filename: {filename} From url: {url}")
        return filename

    def __get_output_path(self, url: str, output_file: str) -> str:
        if os.path.isdir(output_file):
            filename = self.__get_filename_from_url(url)
            return os.path.join(output_file, filename)
        return output_file

    def __basic(self):
        output_file = self.__get_output_path(self.__base_url, self.__output_file)
        self.__make_request(self.__base_url, output_file)

    def __spider(self):
        self.__sub_urls = self.__make_request(self.__base_url, self.__output_file)
        for url in self.__sub_urls:
            print(url)

    def __recursive(self):
        pass

    def set_url(self, url: str):
        self.__base_url = url
        self.__logger.info(f"Url set to: {self.__base_url}")

    def set_output_file(self, output_file: str):
        self.__output_file = os.path.abspath(output_file)
        self.__logger.info(f"Output file set to: {self.__output_file}")

    def set_debug_mode(self, debug_mode: bool):
        if debug_mode:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(self.__formatter)
            self.__logger.addHandler(stream_handler)
            self.__logger.setLevel(logging.DEBUG)

    def set_spider(self, spider_mode: bool):
        if spider_mode:
            self.__spider_mode = True
        self.__logger.debug(f"Spider mode: {self.__spider_mode}")

    def set_recursive(self, recursive_mode: bool):
        if recursive_mode:
            self.__recursive_mode = True
        self.__logger.debug(f"Recursive mode: {self.__recursive_mode}")

    def set_depth_level(self, level: int):
        self.__depth_level = level
        self.__logger.debug(f"Depth level: {self.__depth_level}")

    def set_tries(self, tries: int):
        self.__tries = tries
        self.__logger.debug(f"Max number of tries per url: {self.__tries}")

    def set_logfile(self, logfile):
        print(logfile)
        if type(logfile) == str:
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(self.__formatter)
            if self.__logger.level != logging.DEBUG:
                self.__logger.setLevel(logging.DEBUG)
            self.__logger.addHandler(file_handler)

    def start(self):
        if self.__recursive_mode and self.__spider_mode:
            self.__logger.critical("Can't go in recursive and spider at the same time")
        elif self.__spider_mode:
            self.__logger.info("Running Spider mode")
            self.__spider()
        elif self.__recursive_mode:
            self.__logger.info("Running Recursive mode")
            self.__recursive()
        else:
            self.__logger.info("Running Basic mode")
            self.__basic()


def get_args():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-o", "--output-file",
                                 help="The filename/folder which/where you want to download the arget url",
                                 default=".")
    argument_parser.add_argument("-d", "--debug",
                                 help="Set to debug mode",
                                 action="store_true",
                                 default=False)
    argument_parser.add_argument("--spider",
                                 help="Map the website",
                                 action="store_true",
                                 default=False)
    argument_parser.add_argument("-r", "--recursive",
                                 help="Download recursively every file (-o, --output-file is considered a directory)",
                                 action="store_true",
                                 default=False)
    argument_parser.add_argument("-l", "--level",
                                 help="Depth level from spider or recursive modes",
                                 type=int, default=5)
    argument_parser.add_argument("-t", "--tries",
                                 help="Number of tries until success per url",
                                 type=int,
                                 default=1)
    argument_parser.add_argument("-O", "--log-file",
                                 help="File to log debbuging",
                                 default=None)
    argument_parser.add_argument("url", help="Target url")
    return vars(argument_parser.parse_args())


def main():
    arguments = get_args()
    handler = Handler()
    handler.set_debug_mode(arguments["debug"])
    handler.set_url(arguments["url"])
    handler.set_output_file(arguments["output_file"])
    handler.set_spider(arguments["spider"])
    handler.set_recursive(arguments["recursive"])
    handler.set_depth_level(arguments["level"])
    handler.set_tries(arguments["tries"])
    handler.set_logfile(arguments["log_file"])
    handler.start()


if __name__ == "__main__":
    main()
