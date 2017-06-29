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
* Install twine
  * If you are in a python virtual environment run `pip3 install twine`
  * Else install globally with `sudo pip3 install twine`
* Send the code to pypi
  * Make sure you have a '~/.pypirc' file with the following contents
```
index-servers =
    pypi

[pypi]
username: byu-oit-appdev
password: <the appropriate password>
```

* Install the dependencies by running `python3 install -r requirements.txt`
* Build the installable artifacts by running `python3 setup.py sdist bdist_wheel`
* After you update the version in setup.py run `twine upload dist/*` to upload to pypi.python.org

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
