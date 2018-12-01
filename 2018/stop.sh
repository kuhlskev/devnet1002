#!/bin/bash
# Prepare environment for DEVNET2449 Lab

vagrant suspend
docker rm -f `docker ps -a -q`
