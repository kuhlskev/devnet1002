#!/bin/bash
# Remove environment for DEVNET1002 Lab

vagrant destroy
docker rm -f `docker ps -a -q`
