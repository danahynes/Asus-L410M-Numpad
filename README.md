<!----------------------------------------------------------------------------->
<!-- Filename: README.md                                       /          \  -->
<!-- Project : Asus_L410M_Numpad                              |     ()     | -->
<!-- Date    : 02/17/2019                                     |            | -->
<!-- Author  : Dana Hynes                                     |   \____/   | -->
<!-- License : WTFPLv2                                         \          /  -->
<!----------------------------------------------------------------------------->

# Asus_L410M_Numpad
## "It mostly works™"

This small program runs at boot and gives you access to the numpad that co-exists with the L410M trackpad.
The code is largely inspired by [this project](https://gitlab.com/Thraen/gx735_touchpad_numpad).

![](numpad.jpg)

# Installing

To install, clone the git repo:
```bash
foo@bar:~$ cd ~/Downloads
foo@bar:~$ git clone https://github.com/danahynes/Asus_L410M_Numpad
foo@bar:~$ cd Asus_L410M_Numpad
```

You will need to install the python3 module 'libevdev':
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ pip3 install libevdev
```

Once you do that, you can install by:
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ sudo ./install.sh
```
You can also download the [latest release](http://github.com/danahynes/Asus_L410M_Numpad/releases/latest), unzip it, and run the install.sh file from there.

# Uninstalling

To uninstall, go to the git directory and run:
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ sudo ./uninstall.sh
```

or delete the files manually:
```bash
foo@bar:~$ sudo rm /usr/bin/asus_l410m_numpad.py
foo@bar:~$ sudo rm /lib/systemd/system/asus_l410m_numpad.service
```

# Notes

I have not been able to get the backlight for the numpad working yet. I thought it would be mapped to the keyboard's NUMLOCK light, as it was in [the original project](https://gitlab.com/Thraen/gx735_touchpad_numpad), even though my keyboard doesn't actually have one. Testing shows the messages for the light are being sent and tracked by the system, but the hardware doesn't work yet. More testing with a working (Windows) installation and a USB sniffer is needed, but I'm WAAAAYYY too lazy to do that.

Also note that this only works IF YOUR NUMLOCK KEY IS OFF AT BOOT. Mine is, yours probably will be too, but since I don't have a reliable way to get the numlock state at boot (still futzing with X on this -),  it is assumed that it is off. Again, this will be the default state for most users, so you should be OK. IF YOUR NUMLOCK KEY IS ON AT BOOT, I can't guarantee the behavior, so YMMV.

This program assumes that when it starts, NUMLOCK will be off (as it should at system boot). Checking the state of the numlock at start has proven quite difficult, so we assume it is off (as it should be 99% of the time). If your system boots with the NUMLOCK on, please fork, change, and send me a pull request with more info so I can investigate.

# TODO

1. better sync with numlock key/state (including OSK and state at boot)
