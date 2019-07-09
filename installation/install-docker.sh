#!/bin/bash

# Install Docker on the head node
yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2
  
 yum-config-manager --add-repo \ 
  https://download.docker.com/linux/centos/docker-ce.repo
 
 yum install -y docker-ce
 
 systemctl enable docker
 systemctl start docker
 
 # Install Docker on all of the compute nodes
 bexec "yum install -y yum-utils device-mapper-persistent-data lvm2"
 bexec "yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
 bexec "yum install -y docker-ce"
 bexec "systemctl enable docker"
 bexec "systemctl start docker"
