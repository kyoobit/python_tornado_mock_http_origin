# Mock HTTP Origin

Mock HTTP origin is a Python-based web application built using the [Tornado framework](https://www.tornadoweb.org/). It is primarily used for API and configuration development and testing. The application's core function is to include the HTTP request details in its response body. Additionally, it provides several other features that are helpful for bug replication, failover configuration of multi-layer proxy setups, and as a mock API endpoint. You may want to skim through the current options documented in the [help.txt file](https://github.com/kyoobit/python_tornado_mock_http_origin/blob/main/help.txt), navigating to the `.*/help` URL path once the application is running, or see the [application example](https://mock-http-origin.nateroyer.com/help).

See an example response [in your browser](https://mock-http-origin.nateroyer.com/example), or by using an HTTP client like `curl`:

    curl -i https://mock-http-origin.nateroyer.com/an/example

An example of a JSON formatted response:

    curl -i --header 'Accept: text/json' https://mock-http-origin.nateroyer.com/another/example

Build your own image from the [github repository](https://github.com/kyoobit/mock_http_origin) or run a container via the [github container repository](https://github.com/kyoobit/python_tornado_mock_http_origin/pkgs/container/tornado-mock-http-origin) directly:

    docker pull ghcr.io/kyoobit/tornado-mock-http-origin:latest
    docker run --rm --detach --tty --publish 8888:8888/tcp \
    --name mock-http-origin tornado-mock-http-origin:latest

Use the container as a local test endpoint:

    curl -i 'http://127.0.0.1:8888/a/container?status=234&reason=Example'

Example "234 Example" response from the curl show above:

```
HTTP/1.1 234 Example
Server: Python/Tornado/Mock_HTTP_Origin/0.12.1a
Content-Type: text/plain
Date: Sun, 12 Nov 2023 18:32:39 GMT
Cache-Control: private, no-store
X-Status-Code: 234 set by query string
Content-Length: 0
```

## Docker Image Build

Clone the project

    git clone https://github.com/kyoobit/python_tornado_mock_http_origin

Move into the `python_tornado_mock_http_origin` directory

    cd python_tornado_mock_http_origin

Build the image:

    docker build --tag tornado-mock-http-origin:latest .

Run the container:

    docker run --rm --detach --tty --publish 8888:8888/tcp \
    --name mock-http-origin tornado-mock-http-origin:latest

Use the container:

    curl -i http://127.0.0.1:8888/a/local/container
