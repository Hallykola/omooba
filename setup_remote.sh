# Script not tested for the yes and no input
#https://github.com/Hallykola/MetaTrader5-Docker-Image

wget https://github.com/Hallykola/MetaTrader5-Docker-Image/archive/refs/heads/main.zip
sudo apt update -y
sudo apt install zip -y
unzip main.zip
cd MetaTrader5-Docker-Image-main

#install docker
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin  -y

sudo docker build -t mt5 .
sudo docker run -d -p 3000:3000 -p 8001:8001 -v config:/config mt5
sudo docker ps

sudo docker exec -it 210789b2da17 bin/bash

cd config
sudo apt update
sudo apt install zip -y
sudo unzip trader4.zip

sudo apt install pip -y
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
cd trader4
pip3 install -r requirements.txt
python3 -m pip install -r requirements.txt

sudo rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/Africa/Lagos /etc/localtime
nohup python main.py &

#  nohup ./yourscript &


cat nohup.out
ps -ef | grep python



cd config
rm -r trader4.zip
rm -r trader4

# gwT1r6qTGoNrZM?