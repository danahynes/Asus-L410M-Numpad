#! /bin/bash
sudo cp ./gx735_touchpad_numpad.py /usr/bin
sudo cp ./gx735_touchpad_numpad.service /lib/systemd/system/
sudo systemctl enable gx735_touchpad_numpad