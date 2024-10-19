import json

import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerFootballPaths(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def boilerplate(self, response, **kwargs):
        # Check response code for the expected value
        assert response.code == kwargs.get("code")

        # Check response headers for expected values
        assert response.headers.get("Server").startswith("Python/Tornado")
        assert response.headers.get("Cache-Control") == "private, no-store"
        assert response.headers.get("Content-Type") == "image/svg+xml"
        if kwargs.get("method") != "HEAD":
            assert int(response.headers.get("Content-Length")) == kwargs.get(
                "content_length"
            )

        # Check response body for expected values
        if kwargs.get("method") != "HEAD":
            assert len(response.body) == kwargs.get("body_length")

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="GET",
            headers={"Accept-Encoding": "identity"},
            decompress_response=False,
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="GET",
            content_length=1384,
            body_length=1384,
        )
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="GET",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="GET",
            content_length=795,
            body_length=1384,
        )
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="HEAD",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="HEAD",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="POST",
            headers={"Accept-Encoding": "identity"},
            body="test",
            decompress_response=False,
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="GET",
            content_length=1384,
            body_length=1384,
        )
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/football.svg",
            method="POST",
            headers={"Accept-Encoding": "gzip"},
            body="test",
        )
        boilerplate = self.boilerplate(
            response,
            code=200,
            method="GET",
            content_length=795,
            body_length=1384,
        )
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerHelpPaths(tornado.testing.AsyncHTTPTestCase):
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
            assert response.body.decode().startswith("# Hello World!") is True

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="GET",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="GET",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="HEAD",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="HEAD",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="POST",
            headers={"Accept-Encoding": "identity"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/help",
            method="POST",
            headers={"Accept-Encoding": "gzip"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerPingPaths(tornado.testing.AsyncHTTPTestCase):
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
            assert response.body == b"pong\n"

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="GET",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="GET",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="HEAD",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="HEAD",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="POST",
            headers={"Accept-Encoding": "identity"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ping",
            method="POST",
            headers={"Accept-Encoding": "gzip"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerHelloWorldPaths(tornado.testing.AsyncHTTPTestCase):
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
            assert response.body == b"Hello, World!\n"

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="GET",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="GET",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="HEAD",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="HEAD",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="POST",
            headers={"Accept-Encoding": "identity"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/hello_world",
            method="POST",
            headers={"Accept-Encoding": "gzip"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerEndsWithJSONPaths(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def boilerplate(self, response, **kwargs):
        # Check response code for the expected value
        assert response.code == kwargs.get("code")

        # Check response headers for expected values
        assert response.headers.get("Server").startswith("Python/Tornado")
        assert response.headers.get("Cache-Control") == "private, no-store"
        assert response.headers.get("Content-Type") == "text/json"
        if kwargs.get("method") != "HEAD":
            assert int(response.headers.get("Content-Length")) > 0

        # Check response body for expected values
        if kwargs.get("method") != "HEAD":
            assert len(response.body) > 0
            body = json.loads(response.body.decode())
            assert body["request"]["path"] == "/test/ends/with.json"
            assert body["response"]["status_code"] == 200
            assert ["Content-Type", "text/json"] in body["response"]["headers"]

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="GET",
            headers={
                "Accept-Encoding": "identity",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="GET",
            headers={
                "Accept-Encoding": "gzip",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="HEAD",
            headers={
                "Accept-Encoding": "identity",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="HEAD",
            headers={
                "Accept-Encoding": "gzip",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="POST",
            headers={
                "Accept-Encoding": "identity",
            },
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/ends/with.json",
            method="POST",
            headers={
                "Accept-Encoding": "gzip",
            },
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerJSONPaths(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(debug=True, autoreload=False)

    def boilerplate(self, response, **kwargs):
        # Check response code for the expected value
        assert response.code == kwargs.get("code")

        # Check response headers for expected values
        assert response.headers.get("Server").startswith("Python/Tornado")
        assert response.headers.get("Cache-Control") == "private, no-store"
        assert response.headers.get("Content-Type") == "text/json"
        if kwargs.get("method") != "HEAD":
            assert int(response.headers.get("Content-Length")) > 0

        # Check response body for expected values
        if kwargs.get("method") != "HEAD":
            assert len(response.body) > 0
            body = json.loads(response.body.decode())
            assert body["request"]["path"] == "/test/accept/json.ext"
            assert body["response"]["status_code"] == 200
            assert ["Content-Type", "text/json"] in body["response"]["headers"]

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="GET",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "identity",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="GET",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "gzip",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="HEAD",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "identity",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="HEAD",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "gzip",
            },
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="POST",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "identity",
            },
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/accept/json.ext",
            method="POST",
            headers={
                "Accept": "text/json",
                "Accept-Encoding": "gzip",
            },
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True


# https://www.tornadoweb.org/en/stable/testing.html
class TestRepeaterHandlerDefaultPaths(tornado.testing.AsyncHTTPTestCase):
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
            assert len(response.body) > 0
            assert response.body.decode().startswith("# Hello World!") is False
            assert (
                response.body.decode().find(
                    f"> {kwargs.get('method')} /test/default/file.ext HTTP/1.1"
                )
                != -1
            )
            if kwargs.get("method") == "POST":
                assert response.body.decode().find("* POST DATA b'test'") != -1

        return True

    def test_HTTP_method_GET_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="GET",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_GET_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="GET",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="GET")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="HEAD",
            headers={"Accept-Encoding": "identity"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_HEAD_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="HEAD",
            headers={"Accept-Encoding": "gzip"},
        )
        boilerplate = self.boilerplate(response, code=200, method="HEAD")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_identity(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="POST",
            headers={"Accept-Encoding": "identity"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True

    def test_HTTP_method_POST_AE_gzip(self):
        # Make the HTTP request
        response = self.fetch(
            "/test/default/file.ext",
            method="POST",
            headers={"Accept-Encoding": "gzip"},
            body="test",
        )
        boilerplate = self.boilerplate(response, code=200, method="POST")
        assert boilerplate is True
