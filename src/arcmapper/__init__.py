import os
import sys
import time
import socket
import logging
import threading
import subprocess
import webbrowser

from waitress import serve
from .app import app
from .arc import read_arc_schema
from .dictionary import read_data_dictionary

__version__ = "0.1.0"

ARCMAPPER_HOST = os.getenv("ARCMAPPER_HOST", "127.0.0.1")
ARCMAPPER_PORT = int(os.getenv("ARCMAPPER_PORT", 8050))
ARCMAPPER_TIMEOUT = 30


def launch_app():
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    serve(app.server, host=ARCMAPPER_HOST, port=ARCMAPPER_PORT)


def launch_subprocess():
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    return subprocess.Popen(
        [
            "waitress-serve",
            "--host",
            ARCMAPPER_HOST,
            "--port",
            str(ARCMAPPER_PORT),
            "arcmapper.app:app.server",
        ]
    )


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def wait_for_server(
    host=ARCMAPPER_HOST, port=ARCMAPPER_PORT, timeout=ARCMAPPER_TIMEOUT
) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if check_port(host, port):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(1)
    raise TimeoutError(f"Server did not start within {timeout} seconds")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--debug", "-d"]:
        print("[DEBUG]")
        app.run_server(debug=True)
        return
    if check_port(ARCMAPPER_HOST, ARCMAPPER_PORT):
        logging.info("Port is already in use. Opening browser.")
        webbrowser.open(f"http://{ARCMAPPER_HOST}:{ARCMAPPER_PORT}")
        return
    # Launch the server in a separate thread
    server_thread = threading.Thread(target=launch_app)
    server_thread.start()
    # Wait for startup before opening web browser
    wait_for_server(
        ARCMAPPER_HOST,
        ARCMAPPER_PORT,
        ARCMAPPER_TIMEOUT,
    )
    print(f"[PROD] Open browser at http://{ARCMAPPER_HOST}:{ARCMAPPER_PORT}")
    # Join the server thread and wait for it to finish or be closed
    server_thread.join()


__all__ = ["read_arc_schema", "map", "read_data_dictionary", "main"]
