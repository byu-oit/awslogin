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
* Make sure you have a '~/.pypirc' file with the following contents
```
index-servers =
    pypi

[pypi]
username: byu-oit-appdev
password: <the appropriate password>
```
* Remove the old dist directory `rm -fr dist`
* Install the dependencies by running `pip install -r requirements.txt`
* Update the version in setup.py
* Build the installable artifacts by running `python setup.py sdist bdist_wheel`
* Send the new version to pypy by running `twine upload dist/*`

## TODO
* (Josh) Alphabetize the account names and roles
* Final login message after selecting role specifying you have been logged into this role on this account
* gracefully handle the error case when the duo push is rejected
* Add support for profiles
* Add flags for account and role
* Authenticate once for 8 hours and rerun `awslogin` to relogin
* (Brett) Maybe add a select account then select role interactive method
* Simplify the adfs authentication code
* cache netid after subsequent logins ie default to last used
* Make a handel-codepipeline CI/CD pipeline with automated tests.  If they pass automatically deploy to pypi.
