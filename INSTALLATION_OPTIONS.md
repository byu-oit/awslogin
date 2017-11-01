# Various tested and working ways of installing byu_awslogin depending on the OS

## node:latest docker image or any debian wheezy installation built in Python
* `apt-get update`
* `apt-get install python-dev`
* `wget https://bootstrap.pypa.io/get-pip.py`
* `python get-pip.py`
* ` install byu_awslogin`
* `awslogin`

## node:latest docker image or any debian wheezy installation with adding Python3
* `echo -e "deb http://ftp.de.debian.org/debian experimental main\ndeb http://ftp.de.debian.org/debian unstable main\n" >> /etc/apt/sources.list`
* `apt-get update`
* `apt-get install python3.6`
* `wget https://bootstrap.pypa.io/get-pip.py`
* `python3.6 get-pip.py`
* `pip3.6 install byu_awslogin`
* `awslogin`


## Another good way
Another good way is to use a project like [pipsi](https://github.com/mitsuhiko/pipsi) which will keep Python cli application dependencies seperated from your global python packages

1. Install pipsi follow their install directions [here](https://github.com/mitsuhiko/pipsi)
2. Install via pipsi: `pipsi install byu_awslogin`
3. To upgrade: `pipsi upgrade byu_awslogin`
