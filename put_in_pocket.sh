#!/bin/sh

# This script is called by a Mail.app rule to process messages containing a link to add to Pocket

# log to the system log
/usr/bin/logger "put_in_pocket: $1"

# run the python script
# replace the path to python with the path to your python installation
# replace the path to the python script with the path to your python script
/Library/Frameworks/Python.framework/Versions/3.11/bin/python /Users/rhet/Dropbox/Code/put-in-pocket/put_in_pocket.py "$1"

# log the exit code
/usr/bin/logger "put_in_pocket: done with exit code $?"
