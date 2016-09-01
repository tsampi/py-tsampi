#!/bin/bash
set -e


# Commands to make kubernetes happy because you cannot set permission bits in the config and readonly means known_hosts cannot be updated
chmod 400 ~/.ssh/id_rsa || echo "Cannot set permsissions on id_rsa for some reason"
chmod 600 ~/.gnupg/gpg.conf &&  chmod 700 ~/.gnupg || echo "cannot set permissions on gnupg dir"

# load gpg private keys if available
gpg --import /gpg_keys/*.key || echo "No gpg keys imported"


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
    cd /code/tsampi_server/
    /var/env/bin/python manage.py migrate
    /var/env/bin/python manage.py createcachetable
}

dev_server() {
    . /var/env/bin/activate
    cd /code/tsampi_server/
    trap 'kill %1; kill %2' SIGINT
    python manage.py celery worker -l INFO 2>&1 | sed -e 's/^/[celery] /' & python manage.py runserver 0:8080 2>&1 | sed -e 's/^/[django] /'

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
    devserver )
        dev_server
    ;;
    *)
        show_help
    ;;
esac
