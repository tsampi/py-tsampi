Clone https://github.com/tsampi/tsampi-0 to a public repo you have write access to
TODO: explain how to use ssh keys in the project for git

Make a gpg key for signing.
TODO: Explain why we need gpg keys


    sudo docker-compose run server setupdb
    sudo docker-compose run server manage createsuperuser
    sudo docker-compose run --service-ports -e TSAMPI_GPG_FINGERPRINT="" -e TSAMPI_CHAIN="git@github.com:readevalprint/tsampi-0.git" server

Go to http://YOURIP:8080
