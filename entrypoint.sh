#!/bin/bash
set -e


# Commands to make kubernetes happy because you cannot set permission bits in the config and readonly means known_hosts cannot be updated
chmod 400 ~/.ssh/id_rsa || echo "Cannot set permsissions on id_rsa for some reason"


# Define help message
show_help() {
    echo """
    Commands
    manage        : Invoke django manage.py commands
    """
}

case "$1" in
    manage )
        cd /code/tsampi_server/
        /var/env/bin/python manage.py "${@:2}"
    ;;
    sandbox )
        rlwrap /code/tsampi-sandbox "${@:2}"
    ;;
    bash )
        bash "${@:2}"
    ;;
    uwsgi )
         /var/env/bin/uwsgi "${@:2}"
    ;;
    *)
        show_help
    ;;
esac
