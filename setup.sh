#!/bin/bash
# Prepare environment for DEVNET1002 Lab

vagrant up
docker run -it --rm --privileged -v$(pwd):/home/docker kuhlskev/ansible_host /bin/sh
