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
        slash = "/"
        (prefix, sep, suffix) = self.path.partition(slash)
        if not(prefix == "" and sep == slash): self.send_error(
            404,
            f'Unexpected partition ({prefix},{sep},{suffix}).'
            f' Expected ("",{slash}, ... )')
        
        root = Path.cwd()
        self.log_message("%s", f'root"{root}"')
        orgRoot = Path(root, "EUCDigitalWorkspace.github.io")
        self.log_message("%s", f'orgRoot"{orgRoot}"')

        resourcePath = None
        for resourceRoot in (orgRoot, root):
            for candidateDir in (
                Path(resourceRoot, suffix), Path(resourceRoot, suffix, "docs")
            ):
                if candidateDir.is_dir():
                    candidatePath = Path(candidateDir, "index.html")
                    if candidatePath.is_file():
                        resourcePath = candidatePath
                        break
            if resourcePath is not None: break
            candidatePath = Path(resourceRoot, suffix)
            if candidatePath.is_file():
                resourcePath = candidatePath
                break

        if resourcePath is None:
            self.log_message("%s", f'resourcePath None')
        else:
            self.log_message("%s", f'resourcePath"{resourcePath}"')
            self.path = str(resourcePath.relative_to(root))
            self.log_message("%s", f'self.path"{self.path}"')

        super().do_GET()

if __name__ == '__main__':
    chdir(Path(__file__).parents[1])
    server = Server(('localhost', 8001), Handler)
    print(server.start_message())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
