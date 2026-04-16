#!/bin/bash

# Install requirements silently
python3 -m pip install psutil gputil --user --quiet

# Launch the UI in the background and disconnect from terminal
nohup python3 ui.py > /dev/null 2>&1 &

# Detach and exit the shell immediately
disown
exit
