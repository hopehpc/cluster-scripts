#!/bin/bash

echo "Getting Python source"
wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
gunzip Python-3.6.8.tgz && tar -xvf Python-3.6.8.tar
cd Python-3.6.8
./configure -prefix=/usr/local/

echo "Installing Python"
sudo make altinstall

sudo yum install -y python36-setuptools
echo "Installing pip3"
sudo easy_install-3.6 pip
