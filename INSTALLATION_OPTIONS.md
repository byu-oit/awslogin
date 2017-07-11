# Various tested and working ways of installing byu_awslogin depending on the OS

## node:latest docker image or any debian wheezy installation
* `echo "deb http://ftp.de.debian.org/debian experimental main
deb http://ftp.de.debian.org/debian unstable main" >> /etc/apt/sources.list`
* `apt-get update`
* `apt-get install python3.6`
* `wget https://bootstrap.pypa.io/get-pip.py`
* `python3.6 get-pip.py`
* `pip3.6 install byu_awslogin`
* `awslogin`
