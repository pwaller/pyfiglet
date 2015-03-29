#!/bin/bash
set -eux
pyfiglet -f $2 "$1" > /tmp/pyfiglet
figlet -d pyfiglet/fonts -f $2 "$1"> /tmp/figlet
vimdiff /tmp/figlet /tmp/pyfiglet
