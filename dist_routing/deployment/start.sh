#!/bin/sh
# Start Gunicorn in the background
gunicorn app:app -b 127.0.0.1:5000 -w 4 --daemon

# Start Nginx in the foreground
nginx -g "daemon off;"
