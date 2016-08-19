FROM ubuntu:14.04

ENV TERM screen-256color

RUN locale-gen --no-purge en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8


RUN apt-get update -qq && \
apt-get install --yes --force-yes python-software-properties software-properties-common && \
add-apt-repository ppa:git-core/ppa -y && \
apt-get update -qq && apt-get --yes --force-yes install gcc \
git \
build-essential \
python3-dev \
python3-pip \
python-pip \
binutils \
libmysqlclient-dev \
python-mysqldb \
mysql-client \
libproj-dev \
libffi-dev \
libssl-dev \
libxml2-dev \
libxslt1-dev \
libncurses5-dev \
curl \
vim \
libpq-dev \
python-virtualenv \
python-pypy.sandbox \
rlwrap


RUN virtualenv -p python3 /var/env/
RUN /var/env/bin/pip install wheel --upgrade

WORKDIR /code/
ADD ./requirements.txt /code/requirements.txt
RUN /var/env/bin/pip install -r /code/requirements.txt

ADD . /code
RUN   /code/entrypoint.sh manage collectstatic --noinput

ENTRYPOINT  /code/entrypoint.sh manage runserver 0.0.0.0:8080
