#!/bin/bash
# Prepare environment for DEVNET1002 Lab

vagrant up rtr1
docker run -it --rm -v$(pwd):/home/docker kuhlskev/ansible_host /bin/sh
