#!/bin/sh

set -e

host="$1"
shift
port="$1"
shift

until nc -z "$host" "$port"; do
    >&2 echo "RabbitMQ is unavailable - sleeping"
    sleep 1
done

>&2 echo "RabbitMQ is up - executing command"
exec "$@"
