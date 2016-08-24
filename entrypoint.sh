#!/bin/bash
set -e


# Commands to make kubernetes happy because you cannot set permission bits in the config and readonly means known_hosts cannot be updated
chmod 400 ~/.ssh/id_rsa || echo "Cannot set permsissions on id_rsa for some reason"


# Define help message
show_help() {
    echo """
    Commands
    manage        : Invoke django manage.py commands
    wsgi          : Run uwsgi
    setupdb  : Create empty database for tsampi
    """
}

setup_db() {
    set +e
    cd /code/tsampi_server/
    /var/env/bin/python manage.py sqlcreate | mysql -U $DATABASE_USER -h db
    set -e
    /var/env/bin/python manage.py migrate
    /var/env/bin/python manage.py createcachetable
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
    setupdb )
        setup_db
    ;;
    *)
        show_help
    ;;
esac
