#!/bin/sh
set -e

# Replace environment variables in nginx.conf
envsubst '${SERVER_DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Execute nginx
exec nginx -g 'daemon off;'
