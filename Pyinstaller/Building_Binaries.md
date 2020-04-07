# How to build the binaries
## Assumptions
 1. Building from a Mac OS Machine
 2. Docker is installed
 3. Access to Windows machine
 4. Need to Use python 3.7 for Windows & Mac builds due to current limitation in PyInstall
 5. Assumes Poetry is already installed in window sand mac

## Steps to Build
1. On Windows in code dir run `poetry install`
2. Run `poetry run pyinstaller --clean -y --dist ./dist/win --workpath %temp% --onefile awslogin.spec` 
3. Copy the `dist\win\awslogin.exe` to the mac `./dist/win`
4. Build Linux Docker Container (Only time only) `cd Pyinstaller/linux && docker build -t byu-awslogin-linuxbuild .`
5. On the mac build machine run `poetry install`
6. From Source Code root run `./binary_build_bundle.sh versionnum`
7. If all crazy magic works then you will have zips and sha256sum.txt inside `./dist/`
8. If it doesn't work well its experimental so :shrug:
