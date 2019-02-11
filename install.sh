#!/usr/bin/env bash
if ! [ $(whoami) = 'root' ]; then
	echo 'please run following command:  sudo -H ./install.sh'
	exit 1
fi

export LANGUAGE='en_US.UTF-8'

export LANG='en_US.UTF-8'

export LC_ALL='en_US.UTF-8'

export LC_CTYPE='en_US.UTF-8'

locale-gen en_US en_US.UTF-8

update-locale LANGUAGE='en_US.UTF-8'
update-locale LANG='en_US.UTF-8'
update-locale LC_ALL='en_US.UTF-8'
update-locale LC_CTYPE='en_US.UTF-8'

service postgresql status  > /dev/null 2>&1
if [ "$?" -gt "0" ]; then
  echo "installing postgres...".

  add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -s -c)-pgdg main"

  wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
     apt-key add -
  apt-get update
  apt-get -y install postgresql-9.5

  sudo -u postgres psql -c  " ALTER USER postgres WITH PASSWORD 'dpe';"
  sudo -u postgres psql -c  " CREATE DATABASE test  WITH OWNER postgres;"
  sudo -u postgres psql -c  " CREATE DATABASE pro  WITH OWNER postgres;"
else
  echo "postgres has been Installed"
fi
apt-get update
echo 'install python & pip 3 ...'
apt-get -y install python3-dev python3-pip libxslt1-dev libxml2-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev python3-psycopg2 xvfb qt5-default libqt5network5 libqt5webkit5-dev
echo 'done.'
pip3 install -U pip
echo 'install python requirements ...'
pip3 install --ignore-installed -r requirements.txt
echo 'done.'
