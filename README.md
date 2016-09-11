# INSTALL 

## Get the tsampi_chain
Clone https://github.com/tsampi/tsampi-0 to a public repo you have write access to

Clone this repo

    $ git clone git@github.com:tsampi/py-tsampi.git 
    $ cd py-tsampi
    $ mkdir docker_home   # where ssh and gpg keys are stored.
    
Make sure the container can access your forked tsampi-chain (tsampi-0) from above. 
See [https://git-scm.com/book/en/v2/Git-on-the-Server-Generating-Your-SSH-Public-Key](https://git-scm.com/book/en/v2/Git-on-the-Server-Generating-Your-SSH-Public-Key)

    $ docker-compose run server bash
    root@tsampi:/code# git clone [YOUR FORKED TSAMPI CHAIN] test-chain     # from within the container
    root@tsampi:/code# rm -rf test-chain
    root@tsampi:/code# exit  # leave the container
    
## Make and export your GPG key
From within the container generate a gpg key and export it in ascii armor it to `~/gpg_keys/pub.key` (which is mounted from  `docker_home` created above). See [http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.html](http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.html)
    
    $ docker-compose run server bash
    root@tsampi:/code# gpg --gen-key  # select defaults
    ...
    root@tsampi:/code# gpg --list-secret-keys --fingerprint 
    /root/.gnupg/secring.gpg
    ------------------------
    sec   2048R/C576112D 2016-09-10
          Key fingerprint = 41BE 4B2B C511 6A07 16E2  960F B27D 57E8 C576 112D
    uid                  your name
    ssb   2048R/B48AD64C 2016-09-10

    
    root@tsampi:/code# gpg --export-secret-key  > ~/gpg_keys/private.key
    root@tsampi:/code# exit
    
## Setup admin and run development server
Set up the database and admin user and run the tsampi web server.

    $ docker-compose run server setupdb
    $ docker-compose run server manage createsuperuser  
    $ export TSAMPI_GPG_FINGERPRINT="41BE 4B2B C511 6A07 16E2  960F B27D 57E8 C576 112D"   # from above ^^ 
    $ export TSAMPI_CHAIN="git@github.com:username/tsampi-0.git"   # Change this to your public tsampi chain from above
    $ docker-compose run -p 8080:8080 -e TSAMPI_GPG_FINGERPRINT -e TSAMPI_CHAIN server  # binds on 0.0.0.0:8080

Go to http://YOURIP:8080 in your browser.

# Trouble shooting
Help! I'm getting 
    django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'db' (111)")
    
Keep trying to start the server, if this is the first time tsampi-server is run, it takes a moment for MySql to start to accept conenctions.
