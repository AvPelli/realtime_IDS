#!/bin/bash

# Install java 8
sudo apt install oracle-java8-installer
sudo apt install oracle-java8-set-default

# Install apache kafka
wget https://downloads.apache.org/kafka/2.5.0/kafka_2.12-2.5.0.tgz
tar xzf kafka_2.12-2.5.0.tgz

# Install apache storm
wget https://downloads.apache.org/storm/apache-storm-2.1.0/apache-storm-2.1.0.tar.gz
tar xzf apache-storm-2.1.0.tar.gz

# Install git
sudo apt install git
git config user.name --global "Arthur Van Pellicom"
git config user.email --global "arthur.van.pellicom@hotmail.com"

# Clone project
git clone https://github.com/AvPelli/realtime_IDS.git

