#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: uninstall.sh                                         /          \  #
# Project : Asus_L410M_Numpad                                   |     ()     | #
# Date    : 02/17/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# NB: doesn't matter if run as sudo or not

# show some progress
# NB: first call with sudo to ask for password on its own line (aesthetics)
sudo echo "Uninstalling Asus_L410M_Numpad... "

# stop service now and on reboot
echo "Stopping service... "
sudo systemctl stop asus_l410m_numpad
sudo systemctl disable asus_l410m_numpad
echo "Done"

# delete files from location
echo -n "Deleting files... "
sudo rm -rf /usr/bin/asus_l410m_numpad.py
sudo rm -rf /lib/systemd/system/asus_l410m_numpad.service
sudo rm -rf /var/log/asus_l410m_numpad.log
echo "Done"

# -)
