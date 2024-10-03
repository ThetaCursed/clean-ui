#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
cd ..


if [ -d venv-ui/ ]
then
echo "Found a virtual environment" 
source venv-ui/bin/activate
else 
echo "Please setup the project first using scripts/linux_setup.sh"
exit 0
fi 

#Run Server using LLAMA
python3 clean-ui.py --llama&

#Open browser?
xdg-open "http://127.0.0.1:8080"

exit 0
