# INSTALL 

## Get the tsampi_chain
Clone https://github.com/tsampi/tsampi-0 to a public repo you have write access to

Clone this repo

    $ git clone git@github.com:tsampi/py-tsampi.git 
    $ cd py-tsampi
    $ mkdir -p docker_home   # where ssh and gpg keys are stored.
    
Make sure the container can access your forked tsampi-chain (tsampi-0) from above. 
See [https://git-scm.com/book/en/v2/Git-on-the-Server-Generating-Your-SSH-Public-Key](https://git-scm.com/book/en/v2/Git-on-the-Server-Generating-Your-SSH-Public-Key)

    $ docker-compose run server bash
    root@tsampi:/code# git clone [YOUR FORKED TSAMPI CHAIN] test-chain     # from within the container
    root@tsampi:/code# rm -rf test-chain
    root@tsampi:/code# exit  # leave the container
    
## Make and export your GPG key
From within the container generate a gpg key and export it in ascii armor it to `/root/gpg_keys/pub.key` (which is mounted from  `docker_home` created above). IMPORTANT: you should back up your private key somewhere.
See [http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.html](http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.html)
    
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

    
    root@tsampi:/code# mkdir -p ~/gpg_keys/
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

# Troubleshooting
> Help! I'm getting 
> `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'db' (111)")`
    
Keep trying to start the server, if this is the first time tsampi-server is run, it takes a moment for MySql to start to accept conenctions.

> No apps are listed, it's just an empty list `[]`.

Check the output for something like `fatal: Could not read from remote repository.` This means that that either you need a to add ssh access to tsampi for this repo or maybe there is a typo in the url. There could be a lot of reasons, too many to mention here. Generally `docker-compose run server bash -c "git clone $TSAMPI_CHAIN /tmp/tmp-chain"` is a good test to show you have at least read access to your `TSAMPI_CHAIN`.

# How do I develop apps or play with the sandbox?

Check out your `TSAMPI_CHAIN` to the home directory from within the container
    
    $ docker-compose run server bash -c "git clone $TSAMPI_CHAIN"
    $ docker-compose run server sandbox --lib_root=./tsampi-0/tsampi/pypy --tmp=./tsampi-0/
    + chmod 600 /root/.gnupg/gpg.conf
    + chmod 700 /root/.gnupg
    + gpg --import /root/gpg_keys/private.key /root/gpg_keys/priv.key
    gpg: key BA046CB8: already in secret keyring
    gpg: key C7CBA01F: already in secret keyring
    gpg: Total number processed: 2
    gpg:       secret keys read: 2
    gpg:  secret keys unchanged: 2
    + echo 'No gpg keys imported'
    No gpg keys imported
    + case "$1" in
    + rlwrap /code/tsampi-sandbox --lib_root=./tsampi-0/tsampi/pypy --tmp=./tsampi-0/
    'import site' failed
    Python 2.7.3 (2.2.1+dfsg-1ubuntu0.3, Sep 30 2015, 17:43:43)
    [PyPy 2.2.1 with GCC 4.8.4] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    And now for something completely differ
    >>>> import tsampi
    >>>> print "hi"
    hi
