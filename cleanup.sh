#!/bin/bash
# Remove environment for DEVNET1002 Lab

vagrant destroy -f
docker rm -f `docker ps -a -q`
