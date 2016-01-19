FROM ubuntu

MAINTAINER Timothy Watts"tim@readevalprint.com"

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
  git \
  python3-dev \
  python3-pip \
  python-pypy.sandbox

RUN pip3 install virtualenv
RUN virtualenv ~/env/

ADD requirements.txt /code/requirements.txt
RUN ~/env/bin/pip install -r /code/requirements.txt

ADD . /code/




