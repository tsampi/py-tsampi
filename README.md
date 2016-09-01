    sudo docker-compose run server setupdb
    sudo docker-compose run server manage createsuperuser
    sudo docker-compose run --service-ports server

Go to http://YOURIP:8080
