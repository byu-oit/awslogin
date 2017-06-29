# awslogin
Python script for CLI and SDK access to AWS via ADFS while requiring MFA access using https://duo.com/



# TODO
* (Josh) Alphabetize the account names and roles
* Final login message after selecting role specifying you have been logged into this role on this account
* gracefully handle the error case when the duo push is rejected
* Add support for profiles
* Add flags for account and role
* Authenticate once for 8 hours and rerun `awslogin` to relogin
* (Brett) Maybe add a select account then select role interactive method
* Simplify the adfs authentication code
* cache netid after subsequent logins ie default to last used
* (Paul) Document the process to upload changes to pypi
