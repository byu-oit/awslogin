# Various tested and working ways of installing byu_awslogin depending on the OS

## Python Installation Options:
  - See <https://www.python.org/downloads/> for a windows installation method.
  - In linux you may be able to use apt, rpm or <https://www.python.org/downloads/>.
  - In Mac you can use homebrew, macports or <https://www.python.org/downloads/>.

## Recommended Install Method
  - It is highly recommended to use an application like [Pipx](https://pipxproject.github.io/pipx/) to install and use python cli applications.
  - Follow the pipx [installation documentation](https://pipxproject.github.io/pipx/installation/) 
  - Once pipx is installed run `pipx install byu_awslogin`
  - To upgrade to a new release of byu_awslogin run `pipx upgrade byu_awslogin`
  - Note: most popular cause for issues with pipx is path. Ensure the correct paths are in your PATH variable
  
## Alternative Install Methods
  - Run `pip3 install byu_awslogin` or `pip install byu_awslogin` as
    appropriate for your python installation

## node:latest docker image or any debian wheezy installation built in Python
* `apt-get update`
* `apt-get install python-dev`
* `wget https://bootstrap.pypa.io/get-pip.py`
* `python get-pip.py`
* `pip install byu_awslogin`
* `awslogin`

## node:latest docker image or any debian wheezy installation with adding Python3
* `echo -e "deb http://ftp.de.debian.org/debian experimental main\ndeb http://ftp.de.debian.org/debian unstable main\n" >> /etc/apt/sources.list`
* `apt-get update`
* `apt-get install python3.6`
* `wget https://bootstrap.pypa.io/get-pip.py`
* `python3.6 get-pip.py`
* `pip3.6 install byu_awslogin`
* `awslogin`
