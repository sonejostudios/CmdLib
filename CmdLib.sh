#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 CmdLib.py
#read
