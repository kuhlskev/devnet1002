#!/bin/bash
# Prepare environment for DEVNET1002 Lab

#vagrant up
docker run -it --rm --privileged -v$(pwd):/home/docker kuhlskev/ansible_vpn:1.0 /bin/sh
