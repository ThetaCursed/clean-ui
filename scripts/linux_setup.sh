#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
cd ..


if [ -d venv-ui/ ]
then
echo "Found a virtual environment" 
source venv-ui/bin/activate
else 
echo "Creating a virtual environment"
#Simple dependency checker that will apt-get stuff if something is missing
# sudo apt-get install python3-venv python3-pip
SYSTEM_DEPENDENCIES="python3-venv python3-pip zip libhdf5-dev"

for REQUIRED_PKG in $SYSTEM_DEPENDENCIES
do
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo "Checking for $REQUIRED_PKG: $PKG_OK"
if [ "" = "$PKG_OK" ]; then

  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."

  #If this is uncommented then only packages that are missing will get prompted..
  #sudo apt-get --yes install $REQUIRED_PKG

  #if this is uncommented then if one package is missing then all missing packages are immediately installed..
  sudo apt-get install $SYSTEM_DEPENDENCIES  
  break
fi
done
#------------------------------------------------------------------------------

python3 -m venv venv-ui
source venv-ui/bin/activate
fi 

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install torch==2.4.1+cu121 --index-url https://download.pytorch.org/whl/cu121
python3 -m pip install torchvision==0.19.1+cu121 --index-url https://download.pytorch.org/whl/cu121

#Run Server using LLAMA
python3 clean-ui.py --llama

exit 0
