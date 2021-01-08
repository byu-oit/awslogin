#!/bin/bash

if [ "$1" == "" ];
then
	echo "Specify version as argument to tag zip files"
	exit 1
fi
version=$1
mac_zip_name="byu-awslogin-macos-${version}.zip"
mac_zip_out="./dist/${mac_zip_name}"
mac_bin_out="./dist/macos"
linux_zip_name="byu-awslogin-linux-${version}.zip"
linux_zip_out="./dist/${linux_zip_name}"
linux_bin_out="./dist/linux"
win_zip_name="byu-awslogin-win-${version}.zip"
win_zip_out="./dist/${win_zip_name}"
win_bin_out="./dist/windows"


#Bundling Windows Binary
echo "Build windows binary and place in ./dist/win"
echo "Windows will be skipped if awslogin.exe isn't there"
echo "Continue? [y/n]"
read choice

if [ "$choice" != "y" ];
then
	echo "aborting"
	exit 1
fi

echo "Generating Requirements file for building"
poetry export -f requirements.txt --output requirements.txt

####### WINDOWS BUILD and BUNDLE ########
echo "Building Windows Binary with Docker Image"
docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows

if [[ -f "${win_bin_out}/awslogin.exe" ]];
then
	if [[ -f ${win_zip_out} ]];
	then
		echo "Cleaning Previous Output"
		rm "${win_zip_out}"
	fi
	echo "Zipping win binary"
	pushd "$win_bin_out"
	zip ../${win_zip_name} awslogin.exe
	popd
else
	echo "Skipping Windows Bundling"
fi


####### MacOS BUILD and BUNDLE ########
echo "Building Mac OS Binary"

poetry run pyinstaller --clean -y --dist "${mac_bin_out}" --workpath /tmp --onefile awslogin.spec

if [[ -f "${mac_zip_out}" ]] 
then
	echo "Cleaning Previous Output"
	rm "${mac_zip_out}"
fi

echo "Ziping/Tarballing mac binary"
pushd "$mac_bin_out"
zip ../${mac_zip_name} awslogin
popd

####### Linux BUILD and BUNDLE ########
echo "Building Linux Binary with Docker Image"
docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux

if [[ -f "${linux_zip_out}" ]]
then
        echo "Cleaning Previous Output"
        rm "${linux_zip_out}"
fi

echo "Ziping/Tarballing mac binary"
pushd "$linux_bin_out"
zip ../${linux_zip_name} awslogin
popd


##### Checksums ######
echo "Generating Checksums"
pushd "./dist"
sha256sum *.zip > sha256sums.txt
popd


##### Clean Requirements File ######
if [[ -f "requirements.txt" ]];
then
	echo "Cleaning requirements.txt"
	rm requirements.txt
fi

echo "Done"
