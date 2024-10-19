import datetime
import gzip
import json
import logging
import random

from pathlib import Path

# https://www.tornadoweb.org/
# python -m pip install --upgrade tornado
import tornado.httpserver
import tornado.gen
import tornado.web

# Silly f-string support
# Fixed in Python 3.12, HURRAY!
NL = "\n"
TB = "\t"
CR = "\r"

# SVG file content
FOOTBALL_SVG = Path(f"{Path(__file__).parent}/football.svg").read_text()

# Help file content
HELP = Path(f"{Path(__file__).parent}/help.txt").read_text()


class JSONEncoderPlus(json.JSONEncoder):
    """Extend the standard JSONEncoder to handle additional object types."""

    def default(self, obj):
        # Decode Python bytes as a utf-8 string
        if isinstance(obj, bytes):
            return obj.decode("utf-8")

        # Format Python datetime objects in ISO format
        # docs.python.org/3/library/datetime.html#datetime.datetime.isoformat
        if isinstance(obj, datetime.datetime):
            return obj.isoformat(timespec="seconds")

        # Format *some* Python Exception as a string
        # docs.python.org/3/library/exceptions.html
        if isinstance(obj, NotImplementedError):
            return str(obj)

        # Otherwise use the default JSONEncoder
        return super().default(obj)


class RepeaterHandler(tornado.web.RequestHandler):
    """Repeat the HTTP request back to the requester"""

    def initialize(self, **kwargs):
        logging.debug(f"RepeaterHandler.initialize - **kwargs: {kwargs!r}")
        self.set_header("Cache-Control", "private, no-store")
        self.set_header("Server", self.settings.get("name"))

    # Allowed HTTP methods
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods

    # Handle DELETE requests
    async def delete(self, **kwargs):
        self.set_status(405)

    # Handle GET requests
    async def get(self, **kwargs):
        """Convenience method to self.repeat"""
        name = "RepeaterHandler.get"
        logging.debug(f"{name} - calling repeat")
        await self.repeat(**kwargs)

    # Handle HEAD requests
    async def head(self, **kwargs):
        """Convenience method to self.repeat"""
        name = "RepeaterHandler.head"
        logging.debug(f"{name} - calling repeat")
        await self.repeat(**kwargs)

    # Handle OPTIONS requests
    async def options(self, **kwargs):
        """Convenience method to self.repeat"""
        name = "RepeaterHandler.options"
        logging.debug(f"{name} - calling repeat")
        await self.repeat(**kwargs)

    # Handle PATCH requests
    async def patch(self, **kwargs):
        self.set_status(405)

    # Handle POST requests
    async def post(self, **kwargs):
        """Convenience method to self.repeat"""
        name = "RepeaterHandler.post"
        logging.debug(f"{name} - calling repeat")
        await self.repeat(**kwargs)

    # Handle PUT requests
    async def put(self, **kwargs):
        self.set_status(405)

    # -------------------------------------------------------------------------

    def content_encoding(
        self,
        content: str,
        content_as_json: dict = None,
        add_headers_only: bool = False,
        **kwargs,
    ):
        """Compress content according to the content encoding requested

        Only supports gzip compression currently.

        content <str>: Response body content.

        content_as_json <dict>: Response body content formatted in a key/value
            dictionary that will be converted to valid JSON and compressed.
            (Default = False)

        add_headers_only <bool>: Used to ONLY add response headers. The content
            payload includes response headers so we need to add the response
            headers early as this is part of the body content which is
            compressed in a second request to this function.
            (Default = False)

        See Also:
        * docs.python.org/3/library/gzip.html
        * developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding
        * developer.mozilla.org/en-US/docs/Glossary/Quality_values
        """
        name = "RepeaterHandler.content_encoding"

        from_query_param = self.request.arguments.get("encoding", False)
        logging.debug(f"{name} - URL query `encoding': {from_query_param!r}")

        from_ae_header = self.request.headers.get("Accept-Encoding", False)
        logging.debug(f"{name} - `Accept-Encoding': {from_ae_header!r}")

        # Use the URL query parameter value ahead of the header value
        accept_encoding = from_query_param or from_ae_header
        logging.debug(f"{name} - accept_encoding: {accept_encoding!r}")

        # Initialize content_as_json as needed
        if content_as_json is None:
            content_as_json = {}

        # Catch no encoding required
        if not accept_encoding:
            return content, content_as_json

        # Use the first value in a list of acceptable encodings
        if isinstance(accept_encoding, list):
            accept_encoding = accept_encoding[0]
            logging.debug(
                f"{name} - accept_encoding list unpacked: {accept_encoding!r}"
            )

        # Decode bytes to string
        if isinstance(accept_encoding, bytes):
            accept_encoding = accept_encoding.decode()
            logging.debug(
                f"{name} - accept_encoding bytes decoded: {accept_encoding!r}"
            )

        # Early escape if a zero length body or no encoding was specified
        logging.debug(f"{name} - self.request.method: {self.request.method!r}")
        if self.request.method in ["OPTIONS"] or not accept_encoding:
            logging.debug(f"{name} - not encoding content")
            return content, content_as_json

        # TODO: sort list for different quality levels (Q values)
        # https://developer.mozilla.org/en-US/docs/Glossary/Quality_values

        # Process the encodings
        for encoding in [v.strip() for v in accept_encoding.split(",")]:
            logging.debug(f"{name} - encoding: {encoding!r}")

            # Handle Q values ---> 'Accept-Encoding: gzip;q=0.5'
            quality_value = 1  # default when not set
            if encoding.find(";q=") != -1:
                quality_value = float(encoding.split(";q=")[-1])
            logging.debug(f"{name} - quality_value: {quality_value!r}")

            # Handle gzip encoding ---> 'Accept-Encoding: gzip'
            if encoding.startswith("gzip") and quality_value > 0:
                # Add the expected response headers
                self.set_header("Content-Encoding", "gzip")
                self.set_header("Vary", "Accept-Encoding")

                # Escape early when this is only for adding response headers
                logging.debug(f"{name} - add_headers_only: {add_headers_only}")
                if add_headers_only:
                    logging.debug(f"{name} - not encoding content yet!")
                    return content, content_as_json

                # Encode the content
                logging.debug(f"{name} - encoding content with: {encoding!r}")

                # TODO: Allow different compression levels
                """
                # Placeholder note for more control over the gzip compression
                # https://docs.python.org/3/library/zlib.html
                zlib.compressobj(
                    level=-1,
                    method=DEFLATED,
                    wbits=MAX_WBITS,
                    memLevel=DEF_MEM_LEVEL,
                    strategy=Z_DEFAULT_STRATEGY,
                    zdict,
                    )
                gzip_compress = zlib.compressobj(...)
                content = gzip_compress.compress(str.encode(response))
                content += gzip_compress.flush()
                """

                # Handle encoding `content_as_json'
                logging.debug(f"{name} - `content_as_json' {type(content_as_json)}")
                logging.debug(
                    f"{name} - `content_as_json' length with identity: {len(content_as_json or '')}"
                )
                if content_as_json:
                    # Handle converting `content_as_json' to valid JSON
                    if isinstance(content_as_json, dict):
                        content_as_json = json.dumps(
                            content_as_json,
                            indent=4,
                            separators=(",", ": "),
                            sort_keys=True,
                            cls=JSONEncoderPlus,
                        )
                        content_as_json += "\n"  # pretty trailing line break
                    content_as_json = gzip.compress(content_as_json.encode("utf-8"))
                logging.debug(
                    f"{name} - `content_as_json' length with {encoding}: {len(content_as_json or '')}"
                )

                # Handle encoding content
                logging.debug(f"{name} - `content' {type(content)}")
                logging.debug(
                    f"{name} - `content' length with identity: {len(content)}"
                )
                content = gzip.compress(content.encode("utf-8"))
                logging.debug(
                    f"{name} - `content' length with {encoding}: {len(content)}"
                )

                return content, content_as_json

            # Accept-Encoding: compress
            # TODO: support not implemented yet.

            # Accept-Encoding: deflate
            # TODO: support not implemented yet.

            # Accept-Encoding: br
            # TODO: support not implemented yet.

            # Accept-Encoding: identity
            # TODO: support not implemented yet.

            # Accept-Encoding: *
            # TODO: support not implemented yet.

        # Fail safe return when nothing has matched earlier
        return content, content_as_json

    # -------------------------------------------------------------------------

    def generate_content(self, **kwargs):
        """Generate pseudo random body content

        content <str|list>: Passed through when URL query string key `content'
          is not provided in the request.

        max_content_length <int>: Maximum number of bytes allowed
          Default 10240

        """
        name = "RepeaterHandler.generate_content"

        # Maximum content length allowed, default to 1MiB
        max_content_length = int(kwargs.get("max_content_length", 10240))
        logging.debug(
            f"{name} - max_content_length {type(max_content_length)}: {max_content_length!r}"
        )

        # URL query string value syntax:
        # ?content=[<format>:]<int>[&fill=<str>]
        content_length = self.request.arguments.get("content", False)
        # Unpack a list of values and use the first value ONLY
        if isinstance(content_length, list):
            content_length = content_length[0]
        if isinstance(content_length, bytes):
            content_length = content_length.decode()
        logging.debug(
            f"{name} - content_length {type(content_length)}: {content_length!r}"
        )

        # Catch lack of a `content_length' to work with and exit
        # Pass-through `content' as-is or default to an empty list
        if not content_length:
            return kwargs.get("content", [])

        # TODO: Lipsum
        if content_length.lower().startswith("lipsum:"):
            raise NotImplementedError("...yet")
        # TODO: ASCII ART
        elif content_length.lower().startswith("ascii:"):
            raise NotImplementedError("...yet")
        else:
            content_length = int(content_length)
        logging.debug(
            f"{name} - content_length {type(content_length)}: {content_length!r}"
        )

        # Enforce a maximum content limit
        if content_length > max_content_length:
            logging.debug(f"{name} - content_length too large!")
            content_length = max_content_length
            logging.debug(
                f"{name} - using max_content_length as content_length: {content_length!r}"
            )

        # Fill pattern to use with generating content
        default_fill_pattern = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        )
        fill_pattern = self.request.arguments.get("fill", default_fill_pattern)
        # Unpack a list of values and use the first value ONLY
        if isinstance(fill_pattern, list):
            fill_pattern = fill_pattern[0]
        if isinstance(fill_pattern, bytes):
            fill_pattern = fill_pattern.decode()
        logging.debug(f"{name} - fill_pattern {type(fill_pattern)}: {fill_pattern!r}")

        # List of lines to gather body content
        generated_content = []

        # Generate random content until content length is correct
        while len("".join(generated_content)) < content_length:
            # bandit security scan raises B311 for a blacklisted call of random
            # CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
            # https://bandit.readthedocs.io/en/1.7.10/blacklists/blacklist_calls.html#b311-random
            # NOTE: The following use of random.randint is not used in any
            # security context. It is only used to choose a pseudo random
            # value from the available list of characters.
            generated_content.append(
                fill_pattern[random.randint(0, (len(fill_pattern) - 1))]  # nosec B311
            )
        logging.debug(
            f"{name} - generated_content {type(generated_content)}: length={len(generated_content)}"
        )

        # TODO: Handle 'Transfer-Encoding: chunked'
        """
        logging.debug(f"{name} - kwargs.get('transfer-encoding'): \
            {kwargs.get('transfer-encoding')}")
        if kwargs.get('transfer-encoding') == 'chunked':
            chunks = []
            chunk_length = 64
            # Allow chunk_length to be set by a argument
            if self.request.arguments.get('chunk_length', False):
                chunk_length = \
                    int(self.request.arguments.get('chunk_length', 64)[0])
            logging.debug(f"generate_content - chunk_length: {chunk_length!r}")
            for index in range(0, len(output), chunk_length):
                chunk = ''.join(output[index : index + chunk_length])
                # length of bytes sent to hexadecimal
                # remove 0x to uppercase with '\r\n'
                chunks.append(f"{hex(len(chunk)).replace('0x','').upper()}{CR}{NL}")
                # data with '\r\n'
                chunks.append(f"{chunk}{CR}{NL}")
            # Allow this to contain no end of content for some reason
            if not self.request.arguments.get('no_end_of_content', False):
                chunks.append(f"0{CR}{NL}") # end of content
                chunks.append(f"{CR}{NL}") # end of message
            # Set the output to the chunks
            output = chunks
            # Set X-Accel-Buffering: no (proxy_buffering off)
            # nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering
            self.set_header('X-Accel-Buffering', 'no')
        """

        # Return the generated content
        return "".join(generated_content)

    # -------------------------------------------------------------------------

    def prepend_help_text(self, content: str, **kwargs) -> str:
        """Prepend HELP content to the current body content

        content <str>: Existing response body content.

        """
        name = "RepeaterHandler.prepend_help_text"

        logging.debug(f"{name} - content {type(content)}: length={len(content)}")

        # Prepend each line in HELP with a comment mark and space ('# ')
        help_message = []
        for line in HELP.strip().split("\n"):
            help_message.append(f"# {line}{NL}")

        # Prepend the help text to the current content
        content = f"{''.join(help_message)}{NL}{content}"

        logging.debug(f"{name} - content {type(content)}: length={len(content)}")

        return content

    # -------------------------------------------------------------------------

    def modify_status_code(self, **kwargs) -> str:
        """Modify the HTTP status code"""
        name = "RepeaterHandler.modify_status_code"
        logging.debug(f"{name} - self.get_status(): {self.get_status()!r}")
        logging.debug(
            f"{name} - match `status' query parameter: {self.request.arguments.get('status', False)!r}"
        )
        logging.debug(
            f"{name} - match `reason' query parameter: {self.request.arguments.get('reason', False)!r}"
        )
        if self.request.arguments.get("status", False):
            new_status = self.request.arguments.get("status")
            if isinstance(new_status, list):
                new_status = new_status[0]
            new_status = int(new_status)
            logging.debug(f"{name} - new_status: {new_status!r}")

            # Allow the reason test to be set
            if self.request.arguments.get("reason", False):
                new_reason = self.request.arguments.get("reason")[0]
            else:
                new_reason = None
            logging.debug(f"{name} - new_reason: {new_reason!r}")

            self.set_status(new_status, new_reason)
            logging.debug(f"{name} - self.get_status(): {self.get_status()!r}")

            # Also set a response header noting the change in the status code
            self.set_header("X-Status-Code", f"{new_status} set by query string")

        # TODO: The HTTP version used should not be static
        # TODO: _reason attr should not be used directly
        return f"< HTTP/1.1 {self.get_status()} {self._reason}"

    # -------------------------------------------------------------------------

    def modify_response_headers(self, **kwargs) -> tuple:
        """Modify the HTTP response headers"""
        name = "RepeaterHandler.modify_response_headers"
        logging.debug(
            f"{name} - match `header' query parameter: {self.request.arguments.get('header', [])!r}"
        )

        content = kwargs.get("content", "")
        content_as_json = kwargs.get("content_as_json", False)

        # Set or clear response headers as requested
        for header in self.request.arguments.get("header", []):
            header = header.decode("utf8").split(":", 1)
            logging.debug(f"{name} - header: {header!r}")
            if len(header) == 2 and header[1] != "":
                self.set_header(*header)
            else:
                self.clear_header(header[0])

        # Append the response header to the response content
        response_headers = []
        if content_as_json:
            content_as_json["response"]["headers"] = []
        # Order the response headers so this is easier for humans
        for name, value in sorted(self._headers.get_all()):
            response_headers.append(f"< {name}: {value}")
            # Append the response header to the JSON content
            if content_as_json:
                content_as_json["response"]["headers"].append((name, value))
        response_headers = sorted(response_headers)

        # Append the response headers to the plain test content
        content += response_headers

        return content, content_as_json

    # -------------------------------------------------------------------------

    def prepare_body_text(self, **kwargs) -> str:
        """Prepare body text content based on the current request"""
        name = "RepeaterHandler.prepare_body_text"
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        content = kwargs.get("content", [])

        # Set some defaults used unless set through request options
        self.set_header("Content-Type", "text/plain")
        self.set_header("Cache-Control", "private, no-store")

        # Collect data to be used instead of text/plain for JSON requests
        logging.debug(f"{name} - Accept: {self.request.headers.get('Accept', '')}")
        logging.debug(
            f"{name} - path.endswith('.json'): {self.request.path.endswith('.json')}"
        )
        if self.request.headers.get("Accept", "").endswith(
            "/json"
        ) or self.request.path.endswith(".json"):
            self.set_header("Content-Type", "text/json")
            logging.debug(f"{name} - prepare content as JSON!")
            content_as_json = {"request": {}, "response": {}}
        else:
            logging.debug(f"{name} - prepare content as TEXT!")
            content_as_json = False
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: {content_as_json!r}"
        )

        # Create a separator line
        separator = "# " + ("=" * 78)

        # Include A LOT more information with `debug'
        logging.debug(
            f"{name} - match `debug' query parameter: {self.request.arguments.get('debug', False)}"
        )
        if self.request.arguments.get("debug", False):
            for key in sorted(
                [
                    "arguments",
                    "body",
                    "body_arguments",
                    "cookies",
                    "files",
                    "full_url",
                    "headers",
                    "host",
                    "host_name",
                    "method",
                    "path",
                    "protocol",
                    "query",
                    "query_arguments",
                    "remote_ip",
                    "request_time",
                    "uri",
                    "version",
                ]
            ):
                if key in ["full_url", "request_time"]:
                    value = getattr(self.request, key)()
                elif key == "headers":
                    value = [h for h in getattr(self.request, key).get_all()]
                else:
                    value = getattr(self.request, key)
                logging.debug(f"{name} - self.request.{key} {type(value)}: {value!r}")
                content.append(f"# DEBUG: request.{key} {type(value)}: {value!r}")

        # TODO: this is not very DRY: de-duplicate the following with the above
        if content_as_json is not False:
            request = {}
            for key in sorted(
                [
                    "arguments",
                    "body",
                    "body_arguments",
                    "cookies",
                    "files",
                    "full_url",
                    "headers",
                    "host",
                    "host_name",
                    "method",
                    "path",
                    "protocol",
                    "query",
                    "query_arguments",
                    "remote_ip",
                    "request_time",
                    "uri",
                    "version",
                ]
            ):
                # Call the function to return the result
                if key in ["full_url", "request_time"]:
                    value = getattr(self.request, key)()
                # Explode the Cookie instance into key/value tuple pairs
                elif key in ["cookies"]:
                    value = [(k, v) for k, v in getattr(self.request, key).items()]
                # Explode the Header instance into key/value tuple pairs
                elif key == "headers":
                    value = [h for h in getattr(self.request, key).get_all()]
                # Use 'body_length' instead of 'body'
                # since POST/PUT data may be large
                elif key == "body":
                    value = len(getattr(self.request, key))
                    key = "body_length"
                else:
                    value = getattr(self.request, key)
                request[key] = value
                logging.debug(
                    f"{name} - content_as_json['request'][{key!r}]: {value!r}"
                )
            content_as_json.update(request=request)

        # Return a pong when asked for a ping
        logging.debug(
            f"{name} - match `pong' endpoint: {self.request.path.endswith('/ping')}"
        )
        if self.request.path.endswith("/ping"):
            # return content, content_as_json
            if content_as_json:
                return "pong\n", {"ping": "pong"}
            else:
                return "pong\n", False

        # Return a message when asked for a hello_world
        logging.debug(
            f"{name} - match `hello_world' endpoint: {self.request.path.endswith('/hello_world')}"
        )
        if self.request.path.endswith("/hello_world"):
            # return content, content_as_json
            if content_as_json:
                return "Hello, World!\n", {"Hello": "World!"}
            else:
                return "Hello, World!\n", False

        # Return a svg file when asked for a football.svg
        logging.debug(
            f"{name} - match `football' endpoint: {self.request.path.endswith('/football.svg')}"
        )
        if self.request.path.endswith("/football.svg"):
            self.set_header("Content-Type", "image/svg+xml")
            # return content, content_as_json
            return FOOTBALL_SVG, False

        logging.debug(f"{name} - content {type(content)}: length={len(content)}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')}"
        )

        # Include more information with /help or when not `quiet'
        if self.request.path.endswith("/help") or not self.request.arguments.get(
            "quiet", False
        ):
            # Include a leading separator
            content.append(separator)
            # Include the time of the request per this moment
            now = str(datetime.datetime.now(datetime.timezone.utc).isoformat()).rsplit(
                ".", 1
            )[0]
            content.append(
                f"# Headers received and returned for this request at: {now} UTC"
            )
            # Note late additions
            content.append(
                "# NOTE: `Etag' and `Content-Length' response headers are omitted"
            )
            # Note the use of a downstream proxy
            if self.settings.get("proxied", False):
                content.append(
                    "# NOTE: The `Forwarded' request header was set by a local proxy"
                )
            # Note that the /help endpoint exists, when not /help
            if not self.request.path.endswith("/help"):
                content.append("# Try /help for more information")
            # Include a separator
            content.append(separator)
            # Include a line break before the header content
            content.append("")

        # Note some lengths
        logging.debug(f"{name} - content {type(content)}: length={len(content)}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')}"
        )

        # Append the request line
        content.append(
            f"> {self.request.method} {self.request.uri} {self.request.version}"
        )

        # Append the request headers to the content
        # TODO: This is not very DRY: already performed for `content_as_json'
        request_host_header = None
        request_headers = []
        for hdr_name, hdr_value in self.request.headers.get_all():
            # Always set the Host header first in the list (HTTP/1.0)
            if hdr_name.lower() == "host":
                request_host_header = [f"> {hdr_name}: {hdr_value}"]
            else:
                request_headers.append(f"> {hdr_name}: {hdr_value}")
        request_headers = sorted(request_headers)
        request_headers = request_host_header + request_headers
        content += request_headers
        content.append(">")

        # Include POST data provided
        # TODO: This is not very DRY: already performed for `content_as_json'
        if self.request.method == "POST":
            content.append(f"* POST DATA {self.request.body!r}{NL}")

        # Modify the HTTP status code
        content.append(self.modify_status_code())
        if content_as_json:
            content_as_json["response"].update(status_code=self.get_status())
        logging.debug(f"{name} - content {type(content)}: length={len(content)}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')}"
        )

        # Modify the HTTP response headers
        content, content_as_json = self.modify_response_headers(
            content=content,
            content_as_json=content_as_json,
        )
        content.append("<")
        logging.debug(
            f"{name} - content {type(content)}: \
            length={len(content)}"
        )
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: \
            length={len(content_as_json or '')}"
        )

        # Include more information with /help or when not `quiet'
        if self.request.path.endswith("/help") or not self.request.arguments.get(
            "quiet", False
        ):
            # Include a line break after the header content
            content.append("")
            # Include a trailing separator
            content.append(separator)

        # Combine all lines with a trailing line break
        content = "\n".join(content) + "\n"
        logging.debug(f"{name} - content {type(content)}: length={len(content)}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')}"
        )

        # Include more information with /help
        if self.request.path.endswith("/help"):
            content = self.prepend_help_text(content=content)

        # Allow for random content of some length to be generated and used
        # instead of the response content generated above
        content = self.generate_content(content=content)

        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')}"
        )

        return content, content_as_json

    # -------------------------------------------------------------------------

    async def delay_response(self, **kwargs):
        """Allow the response to be delayed"""
        name = "RepeaterHandler.delay_response"
        logging.debug(f"{name} - **kwargs: {kwargs!r}")
        logging.debug(
            f"{name} - match `delay' query parameter: {self.request.arguments.get('delay', False)}"
        )

        content = kwargs.get("content", [])

        if self.request.arguments.get("delay", False):
            delay = self.request.arguments.get("delay")
            if isinstance(delay, list):
                delay = delay[0]
            delay = float(delay)
            logging.debug(f"{name} - delay for {delay!r}")
            logging.debug(f"{name} - delay started...")
            # https://www.tornadoweb.org/en/stable/gen.html#tornado.gen.sleep
            await tornado.gen.sleep(delay)
            logging.debug(f"{name} - delay finished!")
            self.set_header("X-Delay", f"{delay} set by query string")

        return content

    # -------------------------------------------------------------------------

    def set_condition(self, **kwargs):
        """Set a condition to occur only when a value matches"""
        name = "RepeaterHandler.set_condition"
        logging.debug(
            f"{name} - match `set' query parameter: {self.request.arguments.get('set', False)}"
        )

        content = kwargs.get("content", [])

        # Exit early when `set' is not found
        if not self.request.arguments.get("set", False):
            return content

        # Multiple `set' key/value pairs may be passed
        # ? set = <condition : value> , <match : value>
        for set_conditions in self.request.arguments.get("set"):
            set_conditions = set_conditions.decode().split(",")

            # Each `set_conditions' should have at minimum two items:
            # a "condition" and a "match": [<condition>, <match>]
            if len(set_conditions) < 2:
                message = f"{name} - missing arguments: {set_conditions!r}"
                content.append(f"# DEBUG {message}")
                logging.debug(message)
                continue

            # Match condition should be last in the list
            # Match condition should be a <key>:<value> pair
            # Be mindful of IPv6 addresses
            set_match = set_conditions.pop(-1).split(":", 1)
            if len(set_match) != 2:
                logging.debug(f"{name} - `set_match' missing arguments: {set_match!r}")
                continue

            # See if we matched
            matched = False
            set_match_key, set_match_value = set_match
            logging.debug(f"{name} - set_match_key: {set_match_key!r}")
            logging.debug(f"{name} - set_match_value: {set_match_value!r}")

            # Match the request header Host value
            # ?set=delay:4,status:699,host:my-host-value
            host_hdr = str(self.request.headers.get("host")).lower()
            if set_match_key.lower() == "host" and host_hdr == set_match_value.lower():
                matched = True
                logging.debug(f"{name} - matched `host' header: {matched!r}")

            # Match the requesting client's IP address
            # ?set=delay:3,status:599,addr:4.68.48.225
            elif set_match_key.lower() == "addr":
                # Check the Forwarded request header: `for=<client addr>'
                # Forwarded: for="4.68.48.225";scheme=https;method=GET
                forwarded = self.request.headers.get("Forwarded", False)
                logging.debug(f"{name} - forwarded: {forwarded!r}")
                if forwarded and forwarded.find("for=") != -1:
                    # Remove double quotes and split at semi colons
                    forwarded = forwarded.replace('"', "").split(";")
                    # Unpack the `for' item value as the `client_addr'
                    client_addr = [
                        item.split("=")[-1]
                        for item in forwarded
                        if item.startswith("for")
                    ][0]
                else:
                    client_addr = self.request.remote_ip
                logging.debug(f"{name} - client_addr: {client_addr!r}")
                # Be mindful of IPv6 addresses
                if client_addr.lower() == set_match_value.lower():
                    matched = True
                    logging.debug(f"{name} - matched `addr': {matched!r}")

            # Continue to the next `set' as this `set' did not match
            logging.debug(f"{name} - matched: {matched!r}")
            if not matched:
                continue

            # Set the condition on this request as we did match
            for set_condition in set_conditions:
                logging.debug(f"{name} - set_condition: {set_condition!r}")

                # A `set_condition' should be a <key>:<value> pair
                # Be mindful of IPv6 addresses
                set_condition = set_condition.split(":", 1)
                if len(set_condition) != 2:
                    logging.debug(
                        f"{name} - `set_condition' missing arguments: {set_condition!r}"
                    )
                    continue

                set_condition_key, set_condition_value = set_condition
                self.request.arguments[set_condition_key] = set_condition_value
                logging.debug(
                    f"{name} - self.request.arguments[{set_condition_key!r}]: \
                    {self.request.arguments.get(set_condition_key)!r}"
                )

        return content

    # -------------------------------------------------------------------------

    async def repeat(self, **kwargs):
        """Repeat the request made in the response body"""
        name = "RepeaterHandler.repeat"
        logging.debug(f"{name} - **kwargs: {kwargs!r}")

        # Always start with an empty content list
        # Weird issue seen that content was not initiated clean per a request
        content = []
        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")

        # Allow a condition to only be set for a matching condition
        content = self.set_condition(content=content)
        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")

        # Allow the response to be delayed
        content = await self.delay_response(content=content)
        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")

        # Include encoding response headers in the content as requested
        content, content_as_json = self.content_encoding(
            content=content, add_headers_only=True
        )
        logging.debug(
            f"{name} - content {type(content)}: \
            length={len(content)!r}"
        )
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: \
            length={len(content_as_json or '')!r}"
        )

        # Prepare the body content for the response
        # `content_as_json' may be ignored as input at this point
        # since `prepare_body_text' will set it accordingly
        content, content_as_json = self.prepare_body_text(content=content)
        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')!r}"
        )

        # Encode the content as requested
        content, content_as_json = self.content_encoding(
            content=content, content_as_json=content_as_json
        )
        logging.debug(f"{name} - content {type(content)}: length={len(content)!r}")
        logging.debug(
            f"{name} - content_as_json {type(content_as_json)}: length={len(content_as_json or '')!r}"
        )

        # Only include body content with some status codes
        if self.get_status() in [200]:
            # Handle converting `content_as_json' to valid JSON
            if isinstance(content_as_json, dict):
                logging.debug(
                    f"{name} - content_as_json \
                    {type(content_as_json)}: encoding as JSON"
                )
                content_as_json = json.dumps(
                    content_as_json,
                    indent=4,
                    separators=(",", ": "),
                    sort_keys=True,
                    cls=JSONEncoderPlus,
                )
                content_as_json += "\n"  # trailing line break
            # Use `content_as_json' if this is not empty or False
            if content_as_json:
                logging.debug(f"{name} - using `content_as_json' as response `content'")
                content = content_as_json
            # Do not include body content with some request methods
            if self.request.method == "OPTIONS":
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS")
                self.set_header("Access-Control-Allow-Headers", "Origin,Range")
                self.set_header(
                    "Access-Control-Expose-Headers", "Cache-Control,Date,Expires,Server"
                )
                self.set_header("Access-Control-Max-Age", "60")
                self.set_header("Content-Type", "text/plain")
                self.write("")
            # Set Content-Length
            elif self.request.method == "HEAD":
                self.set_header("Content-Length", len(content))
            else:
                self.write(content)


def make_app(**kwargs):
    """Return a Tornado application instance"""
    # tornado.web.Application settings
    # www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
    name = "make_app"
    logging.debug(f"{name} - **kwargs: {kwargs!r}")

    # tornado.web.Application routes
    # www.tornadoweb.org/en/stable/web.html#application-configuration
    routes = kwargs.get(
        "routes",
        [
            (r"/.*", RepeaterHandler),
        ],
    )
    logging.debug(f"{name} - tornado.web.Application routes: {routes!r}")

    # tornado.web.Application settings
    # www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
    app = tornado.web.Application(
        routes,
        autoreload=kwargs.get("debug", False),
        debug=kwargs.get("debug", False),
        compress_response=kwargs.get("compress_response", False),
        allow_ipv6=kwargs.get("allow_ipv6", True),
        name=kwargs.get("name", "Python/Tornado"),
        proxied=kwargs.get("proxied", False),
        version=kwargs.get("version", "0.0.0a"),
    )
    logging.debug(f"{name} - tornado.web.Application app: {app!r}")

    return app


def main(*args, **kwargs):
    """Run a Tornado application server"""
    name = "main"
    logging.debug(f"{name} - *args: {args!r}")
    logging.debug(f"{name} - **kwargs: {kwargs!r}")

    # tornado.web.Application settings
    # www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
    app = make_app(**kwargs)
    logging.debug(f"{name} - tornado.web.Application app: {app!r}")

    # tornado.httpserver.HTTPServer
    # https://www.tornadoweb.org/en/stable/httpserver.html#http-server
    # https://www.tornadoweb.org/en/stable/tcpserver.html
    server = tornado.httpserver.HTTPServer(app)
    address = kwargs.get("address")
    port = int(kwargs.get("port", 8888))
    server.listen(port, address=address)
    try:
        logging.info(f"Started listening at http://{address or '127.0.0.1'}:{port}/")
        server.start(1)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info(f"Stopped listening at http://{address or '127.0.0.1'}:{port}/")
