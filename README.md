# awslogin
Python script for CLI and SDK access to AWS via ADFS while requiring MFA access using https://duo.com/

## Installation 
* Install Python 3.x using your preferred method.  
  * See https://www.python.org/downloads/ for a windows installation method.  
  * In linux you may be able to use apt, rpm or https://www.python.org/downloads/.
  * In Mac you can use homebrew, macports or https://www.python.org/downloads/.
* Run `pip3 install byu-awslogin`

## Usage
* Run `awslogin`

## Deploying changes
* Make sure you have python 3 installed.
* awslogin only works with python 3.
* Enter your [virtualenv](https://virtualenv.pypa.io/en/stable/) using python 3.
* Install twine by running `pip install twine`
* Make sure you have a '~/.pypirc' as defined [here](https://docs.python.org/3.2/distutils/packageindex.html#pypirc). See Paul for the login credentials.
* Run `python deploy.py`


## TODO
* (Josh) Alphabetize the account names and roles
* Final login message after selecting role specifying you have been logged into this role on this account
* gracefully handle the error case when the duo push is rejected
* Add support for profiles
* (Lehi) Add flags for account and role
* Authenticate once for 8 hours and rerun `awslogin` to relogin
* (Brett) Maybe add a select account then select role interactive method
* Simplify the adfs authentication code
* cache netid after subsequent logins ie default to last used
* Write tests
  * (David) adfs_auth.py 
  * (Nate) index.py
  * roles.py
  * assume_role.py
* Make a handel-codepipeline CI/CD pipeline with automated tests.  If they pass automatically deploy to pypi.
