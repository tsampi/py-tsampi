#!/bin/bash
set -e


###### These should be in an init function

# Commands to make kubernetes happy because you cannot set permission bits in the config and readonly means known_hosts cannot be updated
chmod 400 ~/.ssh/id_rsa || echo "Cannot set permsissions on id_rsa for some reason"
chmod 600 ~/.gnupg/gpg.conf &&  chmod 700 ~/.gnupg || echo "cannot set permissions on gnupg dir"

# load gpg private keys if available
gpg --import ~/gpg_keys/*.key || echo "No gpg keys imported"

echo 'github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==
' >>  ~/.ssh/known_hosts

####

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
    # This runs the django runserver and celery worker at the sme time.
    # Not for production use obviously.
    set +e
    cd /code/tsampi_server/
    trap 'kill %1; kill %2' SIGINT
    /var/env/bin/python manage.py celery worker -l INFO  2> >(sed -e 's/^/[celery] /')  & /var/env/bin/python manage.py runserver 0.0.0.0:8080  2> >(sed -e 's/^/[django] /')
    set -e
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
