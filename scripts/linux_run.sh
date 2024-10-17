#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
cd ..

if [ -d venv-ui/ ]
then
 echo "Found a virtual environment" 
 source venv-ui/bin/activate
 #Run Server using LLAMA
 python3 clean-ui.py --llama&
 echo "Waiting for server"
 #Wait for server to wakeup
 sleep 5
 #Open browser?
 echo "Opening browser"
 xdg-open "http://127.0.0.1:8080"
else 
echo "Please setup the project first using scripts/linux_setup.sh"
exit 0
fi 

exit 0
