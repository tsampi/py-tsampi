#!/bin/bash
set -e
set -x

###### These should be in an init function

# Commands to make kubernetes happy because you cannot set permission bits in the config and readonly means known_hosts cannot be updated
chmod -R 600  ~/.ssh/id_rsa || echo "Cannot set permsissions on id_rsa for some reason"
chmod -R 600 ~/.gnupg/gpg.conf &&  chmod 700 ~/.gnupg || echo "cannot set permissions on gnupg dir"

# load gpg private keys if available
gpg --import ~/gpg_keys/*.key || echo "No gpg keys imported"


####

# Define help message
show_help() {
    echo """
    Commands
    manage        : Invoke django manage.py commands
    wsgi          : Run uwsgi
    setupdb  : Create empty database for tsampi
    freeze_dependencies     : freepe pip dependencies and write to requirements.txt
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

pip_freeze() {
    virtualenv -p python3 /tmp/env/
    /tmp/env/bin/pip install -r ./primary-requirements.txt --upgrade
    set +x
    echo -e "###\n# frozen requirements DO NOT CHANGE\n# To update this update 'primary-requirements.txt' then run ./entrypoint.sh pip_freeze\n###" | tee requirements.txt
    /tmp/env/bin/pip freeze | tee -a requirements.txt
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
