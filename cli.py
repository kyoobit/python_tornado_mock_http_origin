import argparse
import logging
import sys

from app import main

__version__ = "0.12.1a"

DEFAULT_NAME = f"Python/Tornado/Mock_HTTP_Origin/{__version__}"

DESCRIPTION = """A Python Tornado mock HTTP origin service which generates a response.
Construction of the response body is influenced by request parameters.
Specific usage options are documented in the "/help" endpoint.

Run the program:

  python3 ./cli.py --debug
  python3 ./cli.py -v --port 8888 --proxied

  curl -i http://127.0.0.1:8888/help
"""

if __name__ == "__main__":
    # Command-Line Arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--address",
        metavar="<ip>",
        help="set the IP address to listen for HTTP requests (default: *)",
    )
    parser.add_argument(
        "--port",
        metavar="<int>",
        type=int,
        default=8888,
        help="set the port to listen for HTTP traffic (default: 8888)",
    )
    parser.add_argument(
        "--name",
        metavar="<str>",
        default=DEFAULT_NAME,
        help=f'set the application "name" used in logging \
               and Server response header (default: {DEFAULT_NAME!r})',
    )
    parser.add_argument(
        "--proxied",
        action="store_true",
        help='enable the "proxied" application state (Default: False)',
    )
    parser.add_argument(
        "--systemd",
        action="store_true",
        help='enable the "systemd" application state (Default: False)',
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=DEFAULT_NAME,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=False,
        help="run with verbose messages enabled (Default: False)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="run with noisy debug messages enabled (Default: False)",
    )

    # Parse all command-line arguments
    argv, remaining_argv = parser.parse_known_args()

    # Add __version__ as an attribute for later reference
    # setattr(argv, "version", __version__)
    argv.version = __version__

    # Configure logging
    # https://docs.python.org/3/howto/logging.html
    if argv.debug:
        log_level = logging.DEBUG
    elif argv.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    if argv.systemd:
        message_fmt = "[app=repeater] %(levelname)s - %(message)s"
    else:
        message_fmt = "[%(asctime)s] %(levelname)s - %(message)s"
    logging.basicConfig(
        format=message_fmt,
        datefmt="%Y-%m-%d %H:%M:%S.%f %Z",
        level=log_level,
    )

    logging.debug(f"{__name__} - sys.argv: {sys.argv}")
    logging.debug(f"{__name__} - argv: {argv}")

    # Not any arguments that may be passed but will be ignored
    if remaining_argv:
        logging.warning(
            f'The following unknown arguments will be ignored: {", ".join(remaining_argv)}'
        )

    # Run the program
    try:
        # Pass all parsed arguments to the app `main` function as key word arguments
        main(**vars(argv))
    except Exception as err:
        logging.error(f"{sys.exc_info()[0]}; {err}")
        # Cause the program to exit on error when running in debug mode
        if hasattr(argv, "debug") and argv.debug:
            raise
