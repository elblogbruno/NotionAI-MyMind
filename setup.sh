#!/bin/sh

if [ `id -u` -ne 0 ]
then
  echo "Please run this script with root privileges!"
  echo "Try again with sudo."
  exit 0
fi

echo "This script will install NotionAI My Mind Server"
echo "NotionAI My Mind will install necessary dependencies for program to work"
echo "Do you wish to continue? (y/n)"

while true; do
  read -p "" yn
  case $yn in
      [Yy]* ) break;;
      [Nn]* ) exit 0;;
      * ) echo "Please answer with Yes or No [y|n].";;
  esac
done

echo ""
echo "============================================================"
echo ""
echo "Installing necessary dependencies... (This could take a while)"
echo ""
echo "============================================================"
apt-get update
apt-get install -y  python-pip git jq python3-pip python3.6
echo "============================================================"
if [ "$?" = "1" ]
then
  echo "An unexpected error occured during apt-get!"
  exit 0
fi



echo ""
echo "============================================================"
echo ""
echo "Cloning project from GitHub.."
echo ""
echo "============================================================"

if ! [ -x "$(command -v pip3)" ]; then
  echo 'Error: PIP software for python3 (pip3) is not installed. I will install it for you!' >&2
  curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
  python3 get-pip.py --user 
fi

git clone https://github.com/elblogbruno/NotionAI-MyMind

cd NotionAI-MyMind/Python-Server/app && pip -r install requirements.txt

if [ "$?" = "1" ]
then
    echo "An unexpected error occured during pip install!"
    exit 0
fi

echo "============================================================"
echo "Setup was successful."
echo "You can run 'python server.py ' to start the server!"
echo "Next steps are configuring the notion credentials!"
echo "============================================================"

sleep 2


exit 0
