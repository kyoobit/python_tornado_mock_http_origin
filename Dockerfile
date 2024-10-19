# podman build --tag tornado-mock-http-origin:v1 .
# podman run --rm --interactive --tty --name mock-http-origin tornado-mock-http-origin:v1 /bin/sh
# podman run --rm --detach --tty --publish 8889:8888/tcp --name mock-http-origin tornado-mock-http-origin:v1
# Use a smaller image
FROM docker.io/library/alpine:latest

# Install the required Python modules
RUN apk add python3 py3-tornado

# Add the Python file to be used
RUN mkdir /mock_http_origin
COPY app.py /mock_http_origin/app.py
COPY cli.py /mock_http_origin/cli.py
COPY football.svg /mock_http_origin/football.svg
COPY help.txt /mock_http_origin/help.txt

# Add a user account
# No need to run as root in the container
RUN addgroup -S appgroup \
    && adduser -S appuser -G appgroup

# Run all future commands as appuser
USER appuser

# Set the command to run on start up
ENTRYPOINT ["python3", "/mock_http_origin/cli.py"]
