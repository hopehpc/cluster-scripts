#!/bin/bash

# Install Singularity from the CentOS/RHEL package
sudo yum update -y && \
        sudo yum install -y epel-release && \
        sudo yum update -y && \
        sudo yum install -y singularity-runtime singularity

# Install Singularity on all of the compute nodes
bexec "sudo yum update -y && \
        sudo yum install -y epel-release && \
        sudo yum update -y && \
        sudo yum install -y singularity-runtime singularity"
