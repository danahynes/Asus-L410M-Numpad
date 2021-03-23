#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: uninstall.sh                                         /          \  #
# Project : Asus_L410M_Numpad                                   |     ()     | #
# Date    : 02/17/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# stop service now and on reboot
sudo systemctl stop asus_l410m_numpad
sudo systemctl disable asus_l410m_numpad

# delete files from location
sudo rm -rf /usr/bin/asus_l410m_numpad.py
sudo rm -rf /lib/systemd/system/asus_l410m_numpad.service
sudo rm -rf /var/log/asus_l410m_numpad.log

# remove dependencies
#sudo apt-get remove python3-libevdev

# -)
