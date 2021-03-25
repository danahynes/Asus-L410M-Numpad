#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: install.sh                                           /          \  #
# Project : Asus_L410M_Numpad                                   |     ()     | #
# Date    : 02/17/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# N.B. doesn't matter if run as sudo or not

# install dependencies
sudo apt-get install python3-libevdev

# copy files to location
sudo cp ./asus_l410m_numpad.py /usr/bin
sudo cp ./asus_l410m_numpad.service /lib/systemd/system/

# start service now and on reboot
sudo systemctl start asus_l410m_numpad
sudo systemctl enable asus_l410m_numpad


# -)
