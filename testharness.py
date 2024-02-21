#
# Standard library imports, in alphabetic order.
#
# Module for HTTP server
# https://docs.python.org/3/library/http.server.html
from http.server import HTTPServer, SimpleHTTPRequestHandler
#
# Module for changing the current directory.
#  https://docs.python.org/3/library/os.html#os.chdir
from os import chdir
#
# Module for OO path handling.
# https://docs.python.org/3/library/pathlib.html
from pathlib import Path
#
# Module for parsing URLs.
# https://docs.python.org/3/library/urllib.parse.html
from urllib.parse import urlparse

slash = "/"

class Server(HTTPServer):
    def start_message(self):
        host, port = self.server_address[0:2] # Items at index zero and one.
        serverURL = "".join((
            'http://', 'localhost' if host == '127.0.0.1' else host, ':',
            str(int(port))
        ))
        return f'Starting HTTP server at {serverURL}\ncwd"{Path.cwd()}"'

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        suffix = self.trim_slash(self.path)
        if suffix is None: return
        self.log_message("%s", f"suffix{suffix}")

        referrerHeader = self.headers.get('Referer')
        referrerURL = (
            None if referrerHeader is None else urlparse(referrerHeader))
        referrer = (
            None if referrerURL is None else
            self.trim_slash(referrerURL.path))
        self.log_message("%s", f"referrer{referrer}")

        resourcePath = None
        root = Path.cwd()
        self.log_message("%s", f'root"{root}"')
        for prefix in (suffix, referrer + suffix):
            if len(prefix) == 0:
                # Request for /
                repository = Path(root, "EUCDigitalWorkspace.github.io")
            else:
                repository = Path(root, prefix[0])
                if repository.is_dir():
                    prefix = prefix[1:]
                else:
                    repository = Path(root, "EUCDigitalWorkspace.github.io")
            repositoryDocs = Path(repository, "docs")
            if repositoryDocs.is_dir(): repository = repositoryDocs
            self.log_message("%s", f'repository"{repository}"')
            candidate = Path(repository, *prefix)
            if candidate.is_dir(): candidate = Path(candidate, "index.html")
            if candidate.is_file():
                resourcePath = candidate
                break

        if resourcePath is None:
            self.log_message("%s", f'resourcePath None')
        else:
            self.log_message("%s", f'resourcePath"{resourcePath}"')
            self.path = str(resourcePath.relative_to(root))
            self.log_message("%s", f'self.path"{self.path}"')

        super().do_GET()

    def trim_slash(self, pathStr):
        (prefix, sep, suffix) = pathStr.partition(slash)
        if not(prefix == "" and sep == slash):
            self.send_error(
                404,
                f'Unexpected partition ({prefix},{sep},{suffix}).'
                f' Expected ("",{slash}, ... )'
            )
            return None
        return tuple() if suffix == "" else tuple(suffix.split(slash))

if __name__ == '__main__':
    chdir(Path(__file__).parents[1])
    server = Server(('localhost', 8001), Handler)
    print(server.start_message())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
