#!/usr/bin/env bash

# Install Docker

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
# apt-cache policy docker-ce # Optional
sudo apt-get install -y docker-ce
# sudo systemctl status docker  # Optional

# Run Docker Without Sudo
sudo usermod -aG docker ${USER}
#su - ${USER}

# Install Docker Compose
sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.16.1/docker-compose-$(uname -s)-$(uname -m)"
sudo chmod +x /usr/local/bin/docker-compose
# docker-compose -v # Optional


# Install Linux Dependencies on Machine


# Install Various Python Packages
