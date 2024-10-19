from datetime import datetime

import pytest

import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithoutParameters(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def boilerplate(self, response, **kwargs):
        # Check response code for the expected value
        assert response.code == kwargs.get("code")

        # Check response headers for expected values
        assert response.headers.get("Server").startswith("Python/Tornado")
        assert response.headers.get("Cache-Control") == "private, no-store"
        assert response.headers.get("Content-Type") == "text/plain"
        if kwargs.get("method") != "HEAD":
            assert int(response.headers.get("Content-Length")) > 0

        # Check response body for expected values
        if kwargs.get("method") != "HEAD":
            assert (
                response.body.decode().find(
                    f"> {kwargs.get('method')} /test/without/parameters.ext HTTP/1.1"
                )
                != -1
            )
            if kwargs.get("method") == "POST":
                assert response.body.decode().find("* POST DATA b'test'") != -1

        return True

    def test_HTTP_method_GET_without_parameters(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/without/parameters.ext",
            method="GET",
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="GET",
        )
        assert boilerplate is True

    def test_HTTP_method_HEAD_without_parameters(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/without/parameters.ext",
            method="HEAD",
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="HEAD",
        )
        assert boilerplate is True

    def test_HTTP_method_POST_without_parameters(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/without/parameters.ext",
            method="POST",
            body="test",
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="POST",
        )
        assert boilerplate is True


@pytest.mark.skip("Not implemented, yet")
# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerTransferEncodingchunked(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_Transfer_Encoding_chunked(self):
        """
        When "content" is combined with a "Transfer-Encoding: chunked" response header
        the response body content will be formatted into a chunked response.
        (Use --raw with curl to view chunked content)

          ?header=transfer-encoding:chunked&content=<int>[&fill=<str>][&chunk_length=<int>][&no_end_of_content=<str>]

          chunk_length=<int> (default: 64) controls the length of each chunk in
            the response generated.

          no_end_of_content=<str> the presence of this attribute will suppress the
            end of content lines ('0\r\n\r\n') in the chunked response. The HTTP
            client will likely hang waiting on the expected end of content lines.
        """
        raise NotImplementedError("...work to do")


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithContentParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_content_no_value(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.body.decode().startswith("# Hello World!") is False
        assert (
            response.body.decode().find("> GET /test/with.ext?content HTTP/1.1") != -1
        )

    def test_HTTP_method_GET_with_content_and_value(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert len(response.body) == 1024

    def test_HTTP_method_GET_with_content_encoding_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024&encoding=identity",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert int(response.headers.get("Content-Length")) == 1024
        assert len(response.body) == 1024

    def test_HTTP_method_GET_with_content_encoding_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024&encoding=gzip",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert int(response.headers.get("Content-Length")) < 1024
        if response.headers.get("X-Consumed-Content-Encoding", False):
            assert len(response.body) == 1024
        else:
            assert len(response.body) < 1024

    def test_HTTP_method_GET_with_content_and_fill(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024&fill=aaaa",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert len(response.body) == 1024
        assert response.body.decode().startswith("aaaaaaaaaaaaaaaaaa") is True

    @pytest.mark.skip("Not implemented yet")
    def test_HTTP_method_GET_with_content_and_lipsum(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024&fill=lipsum",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert len(response.body) == 1024
        assert response.body.decode().startswith("...") is True

    @pytest.mark.skip("Not implemented yet")
    def test_HTTP_method_GET_with_content_and_ascii(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?content=1024&fill=ascii",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert len(response.body) == 1024
        assert response.body.decode().startswith("...") is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithDebugParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_debug(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?debug",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.body.decode().startswith("# DEBUG: request.arguments") is True
        assert response.body.decode().find("> GET /test/with.ext?debug HTTP/1.1") != -1


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithDelayParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_delay(self):
        start_time = datetime.now().isoformat()
        response = self.fetch(
            f"/test/with.ext?delay=1.25&header=X-Start-Time:{start_time}",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.headers.get("X-Delay") == "1.25 set by query string"
        assert response.body.decode().startswith("# Hello World!") is False
        assert response.body.decode().find("< X-Delay: 1.25 set by query string") != -1
        start = datetime.fromisoformat(response.headers.get("X-Start-Time"))
        end = datetime.now()
        delay_delta = end - start
        assert delay_delta.total_seconds() >= 1.25


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithHeaderParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_header_add(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?header=x-wr-test:Test%20add",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.headers.get("X-Wr-Test") == "Test add"
        assert response.body.decode().find("< X-Wr-Test: Test add") != -1

    def test_HTTP_method_GET_with_header_modify(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?header=server:Test%20modify",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.headers.get("Server") == "Test modify"
        assert response.body.decode().find("< Server: Test modify") != -1

    def test_HTTP_method_GET_with_header_remove(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?header=Content-Type:",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert response.headers.get("Content-Type") is None


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithQuiteParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_quite(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?quiet",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 200
        assert (
            response.body.decode().startswith("> GET /test/with.ext?quiet HTTP/1.1")
            is True
        )
        assert response.body.decode().endswith("<\n") is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithSetParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_set_address_match(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?set=delay:0.25,status:599,addr:8.7.6.5",
            method="GET",
            headers={"Forwarded": "for=8.7.6.5"},
        )
        # Check response code for the expected value
        assert response.code == 599
        assert int(response.headers.get("Content-Length")) == 0
        assert response.headers.get("X-Delay") == "0.25 set by query string"
        assert response.headers.get("X-Status-Code") == "599 set by query string"

    def test_HTTP_method_GET_with_set_address_no_match(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?set=delay:0.25,status:599,addr:8.7.6.5",
            method="GET",
            headers={"Forwarded": "for=4.3.2.1"},
        )
        # Check response code for the expected value
        assert response.code == 200
        assert int(response.headers.get("Content-Length")) > 0
        assert response.headers.get("X-Delay") is None
        assert response.headers.get("X-Status-Code") is None

    def test_HTTP_method_GET_with_set_header_match(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?set=delay:0.25,status:599,host:test",
            method="GET",
            headers={"Host": "test"},
        )
        # Check response code for the expected value
        assert response.code == 599
        assert int(response.headers.get("Content-Length")) == 0
        assert response.headers.get("X-Delay") == "0.25 set by query string"
        assert response.headers.get("X-Status-Code") == "599 set by query string"

    def test_HTTP_method_GET_with_set_header_no_match(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?set=delay:0.25,status:599,host:test",
            method="GET",
            headers={"Host": "other"},
        )
        # Check response code for the expected value
        assert response.code == 200
        assert int(response.headers.get("Content-Length")) > 0
        assert response.headers.get("X-Delay") is None
        assert response.headers.get("X-Status-Code") is None


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerWithStatusParameter(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def test_HTTP_method_GET_with_status(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?status=418",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 418
        assert response.reason == "I'm a Teapot"
        assert int(response.headers.get("Content-Length")) == 0
        assert response.headers.get("X-Status-Code") == "418 set by query string"

    def test_HTTP_method_GET_with_status_and_reason(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/with.ext?status=672&reason=Special+Weirdness",
            method="GET",
        )
        # Check response code for the expected value
        assert response.code == 672
        assert response.reason == "Special Weirdness"
        assert int(response.headers.get("Content-Length")) == 0
        assert response.headers.get("X-Status-Code") == "672 set by query string"
